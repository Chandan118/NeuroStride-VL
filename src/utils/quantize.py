"""
NeuroStride-VL: 模型量化与优化模块
====================================
将 PyTorch 模型转换为 TensorRT 引擎以在 Jetson Orin Nano 上加速

功能:
- PyTorch -> ONNX 导出
- ONNX -> TensorRT 引擎转换
- FP16/INT8 量化
- 模型性能基准测试

支持模型:
- SAC/PPO 策略网络 (locomotion policy)
- Qwen-VL 视觉语言模型 (可选)

作者: NeuroStride-VL Team
"""

import os
import time
import json
import argparse
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass, field

import torch
import torch.nn as nn
import numpy as np

# ONNX
import onnx
import onnxruntime as ort

# TensorRT (仅 Jetson 可用)
try:
    import tensorrt as trt
    TRT_AVAILABLE = True
except ImportError:
    TRT_AVAILABLE = False
    print("警告: TensorRT 不可用，仅支持 ONNX 导出")

# 日志
from neurostride.utils.logger import get_logger
log = get_logger(__name__)


@dataclass
class QuantizationConfig:
    """量化配置"""
    # 模型路径
    pytorch_model_path: str = "models/checkpoints/sac_final.zip"
    output_dir: str = "models/trt/"

    # 模型类型
    model_type: str = "policy"  # "policy" or "vl"

    # ONNX 导出配置
    onnx_opset_version: int = 17
    input_names: list = field(default_factory=lambda: ["input"])
    output_names: list = field(default_factory=lambda: ["output"])

    # TensorRT 配置
    precision: str = "fp16"  # "fp32", "fp16", "int8"
    workspace_size: int = 1 << 30  # 1GB
    max_batch_size: int = 1
    min_timing_iterations: int = 10
    avg_timing_iterations: int = 10

    # INT8 量化（需要校准数据）
    calibration_data_path: Optional[str] = None
    num_calibration_batches: int = 100

    # 目标平台
    target_platform: str = "jetson"  # "jetson" or "generic"


class ModelQuantizer:
    """模型量化器"""

    def __init__(self, config: QuantizationConfig):
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.model = None
        self.example_input = None

        log.info(f"ModelQuantizer 初始化: {config.model_type}")

    def load_pytorch_model(self, model_path: str):
        """
        加载 PyTorch 模型

        支持从 Stable-Baselines3 检查点加载
        """
        log.info(f"加载 PyTorch 模型: {model_path}")

        try:
            # 方式1: 从 SB3 检查点加载
            from stable_baselines3 import SAC, PPO
            import neurostride.agents.rl_agent as rl_module

            # 根据模型类型选择算法
            if "sac" in model_path.lower():
                self.model = SAC.load(model_path)
                log.info("从 SAC 检查点加载")
            elif "ppo" in model_path.lower():
                self.model = PPO.load(model_path)
                log.info("从 PPO 检查点加载")
            else:
                # 方式2: 直接加载 state_dict
                checkpoint = torch.load(model_path, map_location="cpu")
                if "policy_state_dict" in checkpoint:
                    # SB3 格式
                    from neurostride.agents.rl_agent import PPOAgent, SACAgent, TrainingConfig
                    config = TrainingConfig(algo="sac")
                    agent = SACAgent(config)
                    agent.policy.load_state_dict(checkpoint["policy_state_dict"])
                    self.model = agent.policy.policy_net
                    log.info("从 SB3 策略网络加载")
                else:
                    raise ValueError("不支持的检查点格式")

            # 获取示例输入
            self.example_input = self._get_example_input()

            log.success(f"模型加载成功！参数量: {sum(p.numel() for p in self.model.parameters()):,}")

        except Exception as e:
            log.error(f"模型加载失败: {e}")
            raise

    def _get_example_input(self) -> torch.Tensor:
        """获取示例输入张量"""
        # 策略网络输入维度 (与训练环境一致)
        obs_dim = 70  # 23(pos) + 23(vel) + 6(imu) + 2(contact) + 3(target_vel) + 3(extra)
        example = torch.randn(1, obs_dim, dtype=torch.float32)
        return example

    def export_to_onnx(self, output_path: str) -> str:
        """
        导出 PyTorch 模型到 ONNX

        Args:
            output_path: ONNX 文件路径

        Returns:
            输出路径
        """
        log.info(f"导出到 ONNX: {output_path}")

        if self.model is None:
            raise ValueError("模型未加载")

        # 设置为评估模式
        self.model.eval()

        # 动态轴（支持可变 batch size）
        dynamic_axes = {
            "input": {0: "batch_size"},
            "output": {0: "batch_size"}
        }

        # 导出
        try:
            torch.onnx.export(
                self.model,
                self.example_input,
                output_path,
                export_params=True,
                opset_version=self.config.onnx_opset_version,
                do_constant_folding=True,
                input_names=self.config.input_names,
                output_names=self.config.output_names,
                dynamic_axes=dynamic_axes,
            )

            # 验证 ONNX 模型
            onnx_model = onnx.load(output_path)
            onnx.checker.check_model(onnx_model)

            log.success(f"ONNX 导出成功: {output_path}")
            log.info(f"  文件大小: {Path(output_path).stat().st_size / 1e6:.2f} MB")

            return output_path

        except Exception as e:
            log.error(f"ONNX 导出失败: {e}")
            raise

    def convert_to_tensorrt(self, onnx_path: str, output_path: str) -> str:
        """
        将 ONNX 转换为 TensorRT 引擎

        Args:
            onnx_path: ONNX 模型路径
            output_path: TensorRT 引擎输出路径

        Returns:
            引擎文件路径
        """
        if not TRT_AVAILABLE:
            log.warning("TensorRT 不可用，跳过转换")
            return ""

        log.info(f"转换为 TensorRT: {output_path}")

        # 创建 TensorRT 日志器
        TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

        # 创建网络定义
        builder = trt.Builder(TRT_LOGGER)
        network = builder.create_network(
            1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
        )

        # 创建配置
        config = builder.create_builder_config()
        config.max_workspace_size = self.config.workspace_size

        # 设置精度
        if self.config.precision == "fp16" and builder.platform_has_fast_fp16:
            config.set_flag(trt.BuilderFlag.FP16)
            log.info("启用 FP16 精度")
        elif self.config.precision == "int8":
            config.set_flag(trt.BuilderFlag.INT8)
            log.info("启用 INT8 精度（需要校准）")

        # 解析 ONNX
        parser = trt.OnnxParser(network, TRT_LOGGER)
        with open(onnx_path, "rb") as f:
            onnx_data = f.read()

        if not parser.parse(onnx_data):
            for error in range(parser.num_errors):
                log.error(f"ONNX 解析错误: {parser.get_error(error)}")
            raise RuntimeError("ONNX 解析失败")

        # 构建引擎
        log.info("构建 TensorRT 引擎...")
        start_time = time.time()
        engine = builder.build_engine(network, config)
        build_time = time.time() - start_time

        if engine is None:
            raise RuntimeError("TensorRT 引擎构建失败")

        # 保存引擎
        with open(output_path, "wb") as f:
            f.write(engine.serialize())

        log.success(f"TensorRT 引擎构建成功: {output_path}")
        log.info(f"  构建时间: {build_time:.2f}s")
        log.info(f"  引擎大小: {Path(output_path).stat().st_size / 1e6:.2f} MB")

        return output_path

    def benchmark_model(
        self,
        model_path: str,
        model_type: str = "onnx",  # "onnx" or "trt"
        num_iterations: int = 1000,
        batch_size: int = 1
    ) -> Dict[str, float]:
        """
        基准测试模型推理速度

        Returns:
            性能指标字典
        """
        log.info(f"基准测试: {model_path}")

        if model_type == "onnx":
            return self._benchmark_onnx(model_path, num_iterations, batch_size)
        elif model_type == "trt":
            return self._benchmark_tensorrt(model_path, num_iterations, batch_size)
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")

    def _benchmark_onnx(
        self,
        onnx_path: str,
        num_iterations: int,
        batch_size: int
    ) -> Dict[str, float]:
        """ONNX 基准测试"""
        session = ort.InferenceSession(
            onnx_path,
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
        )

        input_name = session.get_inputs()[0].name
        input_shape = (batch_size, self.example_input.shape[1])

        # 预热
        for _ in range(10):
            input_data = np.random.randn(*input_shape).astype(np.float32)
            _ = session.run(None, {input_name: input_data})

        # 计时
        latencies = []
        for _ in range(num_iterations):
            input_data = np.random.randn(*input_shape).astype(np.float32)

            start = time.time()
            _ = session.run(None, {input_name: input_data})
            latencies.append((time.time() - start) * 1000)  # ms

        return {
            "mean_latency_ms": np.mean(latencies),
            "p50_latency_ms": np.percentile(latencies, 50),
            "p95_latency_ms": np.percentile(latencies, 95),
            "p99_latency_ms": np.percentile(latencies, 99),
            "throughput_fps": 1000 / np.mean(latencies) * batch_size,
        }

    def _benchmark_tensorrt(
        self,
        engine_path: str,
        num_iterations: int,
        batch_size: int
    ) -> Dict[str, float]:
        """TensorRT 基准测试"""
        with open(engine_path, "rb") as f:
            engine_data = f.read()

        runtime = trt.Runtime(trt.Logger(trt.Logger.WARNING))
        engine = runtime.deserialize_cuda_engine(engine_data)

        # 创建执行上下文
        context = engine.create_execution_context()

        # 分配缓冲区
        inputs, outputs, bindings = self._allocate_buffers(engine, batch_size)

        # 预热
        for _ in range(10):
            self._infer_trt(context, bindings, inputs, outputs)

        # 计时
        latencies = []
        for _ in range(num_iterations):
            start = time.time()
            self._infer_trt(context, bindings, inputs, outputs)
            latencies.append((time.time() - start) * 1000)

        return {
            "mean_latency_ms": np.mean(latencies),
            "p50_latency_ms": np.percentile(latencies, 50),
            "p95_latency_ms": np.percentile(latencies, 95),
            "p99_latency_ms": np.percentile(latencies, 99),
            "throughput_fps": 1000 / np.mean(latencies) * batch_size,
        }

    def _allocate_buffers(self, engine, batch_size: int):
        """为 TensorRT 分配 GPU 缓冲区"""
        inputs = []
        outputs = []
        bindings = []

        for i in range(engine.num_bindings):
            binding_name = engine.get_binding_name(i)
            binding_shape = engine.get_binding_shape(i)
            dtype = trt.nptype(engine.get_binding_dtype(i))

            # 调整 batch 维度
            if binding_shape[0] == -1:
                binding_shape = (batch_size,) + binding_shape[1:]

            # 分配内存
            size = trt.volume(binding_shape)
            host_mem = cuda.pagelocked_empty(size, dtype)
            device_mem = cuda.mem_alloc(host_mem.nbytes)

            bindings.append(int(device_mem))

            if engine.binding_is_input(i):
                inputs.append({"host": host_mem, "device": device_mem})
            else:
                outputs.append({"host": host_mem, "device": device_mem})

        return inputs, outputs, bindings

    def _infer_trt(self, context, bindings, inputs, outputs):
        """执行 TensorRT 推理"""
        # 复制输入到 GPU
        for inp in inputs:
            cuda.memcpy_htod(inp["device"], inp["host"])

        # 执行推理
        context.execute_v2(bindings=bindings)

        # 复制输出回 CPU
        for out in outputs:
            cuda.memcpy_dtoh(out["host"], out["device"])

        return [out["host"] for out in outputs]

    def save_benchmark_report(self, results: Dict[str, Any], path: str):
        """保存基准测试报告"""
        report = {
            "model": self.config.pytorch_model_path,
            "model_type": self.config.model_type,
            "precision": self.config.precision,
            "platform": self.config.target_platform,
            "timestamp": time.time(),
            "metrics": results,
        }

        with open(path, "w") as f:
            json.dump(report, f, indent=2)

        log.info(f"基准测试报告已保存: {path}")


def main():
    parser = argparse.ArgumentParser(description="NeuroStride-VL 模型量化工具")
    parser.add_argument("--input", type=str, required=True, help="输入 PyTorch 模型路径")
    parser.add_argument("--output-dir", type=str, default="models/trt", help="输出目录")
    parser.add_argument("--model-type", type=str, default="policy", choices=["policy", "vl"])
    parser.add_argument("--precision", type=str, default="fp16", choices=["fp32", "fp16", "int8"])
    parser.add_argument("--skip-onnx", action="store_true", help="跳过 ONNX 导出")
    parser.add_argument("--skip-trt", action="store_true", help="跳过 TensorRT 转换")
    parser.add_argument("--benchmark", action="store_true", help="运行基准测试")
    parser.add_argument("--num-iterations", type=int, default=1000, help="基准测试迭代次数")

    args = parser.parse_args()

    # 创建配置
    config = QuantizationConfig(
        pytorch_model_path=args.input,
        output_dir=args.output_dir,
        model_type=args.model_type,
        precision=args.precision,
    )

    quantizer = ModelQuantizer(config)

    try:
        # 1. 加载 PyTorch 模型
        quantizer.load_pytorch_model(args.input)

        # 2. 导出 ONNX
        if not args.skip_onnx:
            onnx_path = quantizer.output_dir / f"{args.model_type}.onnx"
            quantizer.export_to_onnx(str(onnx_path))
        else:
            onnx_path = Path(args.output_dir) / f"{args.model_type}.onnx"

        # 3. 转换为 TensorRT
        if not args.skip_trt and TRT_AVAILABLE:
            trt_path = quantizer.output_dir / f"{args.model_type}_{args.precision}.engine"
            quantizer.convert_to_tensorrt(str(onnx_path), str(trt_path))
        elif not args.skip_trt:
            log.warning("TensorRT 不可用，请确保在 Jetson 上运行")

        # 4. 基准测试
        if args.benchmark:
            log.info("运行基准测试...")

            # ONNX 基准
            onnx_results = quantizer.benchmark_model(
                str(onnx_path), "onnx", args.num_iterations
            )
            log.info(f"ONNX 性能: {onnx_results['mean_latency_ms']:.2f}ms, "
                    f"{onnx_results['throughput_fps']:.1f} FPS")

            # TensorRT 基准（���果可用）
            if TRT_AVAILABLE and not args.skip_trt:
                trt_results = quantizer.benchmark_model(
                    str(trt_path), "trt", args.num_iterations
                )
                log.info(f"TensorRT 性能: {trt_results['mean_latency_ms']:.2f}ms, "
                        f"{trt_results['throughput_fps']:.1f} FPS")

                # 计算加速比
                speedup = onnx_results['mean_latency_ms'] / trt_results['mean_latency_ms']
                log.info(f"加速比: {speedup:.1f}x")

            # 保存报告
            report_path = quantizer.output_dir / "benchmark.json"
            quantizer.save_benchmark_report(
                {"onnx": onnx_results, "trt": trt_results if TRT_AVAILABLE else None},
                str(report_path)
            )

        log.success("量化完成！")

    except Exception as e:
        log.error(f"量化失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

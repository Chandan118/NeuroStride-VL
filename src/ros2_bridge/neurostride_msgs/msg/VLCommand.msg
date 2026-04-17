# VLCommand.msg
# 视觉-语言模型命令

builtin_interfaces/Time stamp

string command                      # 自然语言命令
string action_type                  # 动作类型: "walk", "stop", "avoid"
float32 confidence                  # 置信度 (0-1)

string scene_description            # 场景描述
string[] objects                    # 检测到的物体
string[] hazards                    # 危险列表

string raw_response                 # VLM 原始响应

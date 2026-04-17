"""
NeuroStride-VL Package Configuration
=====================================
Python package build configuration using setuptools
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="neurostride-vl",
    version="0.1.0",
    author="NeuroStride-VL Team",
    author_email="contact@neurostride-vl.ai",
    description="Vision-Language-Action Bipedal Robot Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/NeuroStride-VL",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Robotics",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
        ],
        "ros2": [
            "rclpy>=0.11.0",
            "std_msgs>=0.5.0",
            "geometry_msgs>=0.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "neurostride-train=neurostride.scripts.train:main",
            "neurostride-deploy=neurostride.scripts.deploy:main",
        ],
    },
    include_package_data=True,
)

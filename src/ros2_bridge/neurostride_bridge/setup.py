from setuptools import setup

package_name = 'neurostride_bridge'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    py_modules=[],
    install_requires=['setuptools', 'rclpy'],
    zip_safe=True,
    maintainer='NeuroStride-VL Team',
    maintainer_email='contact@neurostride-vl.ai',
    description='ROS2 bridge nodes for NeuroStride-VL',
    license='MIT',
)

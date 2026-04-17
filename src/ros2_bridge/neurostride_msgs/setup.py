from setuptools import setup

package_name = 'neurostride_msgs'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    py_modules=[],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='NeuroStride-VL Team',
    maintainer_email='your-email@example.com',
    description='Custom messages for NeuroStride-VL bipedal robot framework',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)

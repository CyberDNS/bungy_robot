from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'bungy_policy'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'models', 'rob-s0'), glob('models/rob-s0/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='David Ney',
    maintainer_email='david.ney@live.com',
    description='Learned local planner (ONNX policy from bungy_robot_rl)',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'learned_local_planner = bungy_policy.learned_local_planner:main',
        ],
    },
)

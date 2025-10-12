from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'bungy_bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Install launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        # Install config files
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        # Install urdf files
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.xacro')),
        # Install scripts to lib directory for ROS 2 compatibility
        (os.path.join('lib', package_name), glob(os.path.join(package_name, '*.py'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='david',
    maintainer_email='david@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'twist_to_stamped_relay = bungy_bringup.twist_to_stamped_relay:main',
            'drive_straight_test = bungy_bringup.drive_straight_test:main',
        ],
    },
)
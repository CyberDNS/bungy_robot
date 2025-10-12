from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    package_name = "bungy_bringup"

    # Include robot launch
    robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare(package_name),
                'launch',
                'robot.launch.py'
            ])
        ])
    )

    # Include joystick launch  
    joystick_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare(package_name),
                'launch', 
                'joystick.launch.py'
            ])
        ])
    )

    return LaunchDescription([
        robot_launch,
        joystick_launch,
    ])
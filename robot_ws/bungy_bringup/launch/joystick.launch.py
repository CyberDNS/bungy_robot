import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_name = "bungy_bringup"

    joy_params = PathJoinSubstitution([FindPackageShare(package_name), 'config', 'joystick.yaml'])

    joy_node = Node(
        package='joy',
        executable='joy_node',
        parameters=[joy_params],
    )

    teleop_node = Node(
        package='teleop_twist_joy', 
        executable='teleop_node',
        name='teleop_node',
        parameters=[joy_params],
        remappings=[('/cmd_vel', '/cmd_vel')]  # Output to our twist relay input
    )

    return LaunchDescription([
        joy_node,
        teleop_node,
    ])
#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Package directories
    bungy_monitoring_dir = get_package_share_directory('bungy_monitoring')
    
    # Launch arguments
    robot_ip_arg = DeclareLaunchArgument(
        'robot_ip',
        default_value='192.168.1.100',  # Default robot IP
        description='IP address of the robot'
    )
    
    # Include the main monitoring launch
    monitor_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(bungy_monitoring_dir, 'launch', 'monitor_robot.launch.py')
        ]),
        launch_arguments={
            'rviz_config': os.path.join(bungy_monitoring_dir, 'rviz', 'robot_odom_monitoring.rviz'),
        }.items()
    )

    # Teleop keyboard for remote control
    teleop_keyboard = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_keyboard',
        remappings=[
            ('/cmd_vel', '/cmd_vel')  # This will be converted by the relay on robot
        ],
        output='screen'
    )

    # RQT tools for monitoring
    rqt_graph = Node(
        package='rqt_graph',
        executable='rqt_graph',
        name='rqt_graph',
        output='screen'
    )

    return LaunchDescription([
        robot_ip_arg,
        monitor_launch,
        teleop_keyboard,
        rqt_graph,
    ])
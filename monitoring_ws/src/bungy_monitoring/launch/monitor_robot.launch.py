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
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time'
    )
    
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=os.path.join(bungy_monitoring_dir, 'rviz', 'bungy.rviz'),
        description='Path to RVIZ config file'
    )

    # The robot publishes its own robot_description (/bungy/robot_description) and the TF tree
    # with the 'bungy/' prefix, so RViz needs nothing but the config (RobotModel TF Prefix: bungy).

    # RVIZ node for visualization
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    return LaunchDescription([
        use_sim_time_arg,
        rviz_config_arg,
        rviz_node,
    ])
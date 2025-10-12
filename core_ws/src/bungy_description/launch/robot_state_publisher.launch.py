#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node


def generate_launch_description():
    # Package directories
    bungy_description_dir = get_package_share_directory('bungy_description')
    
    # Launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time'
    )
    
    use_ros2_control_arg = DeclareLaunchArgument(
        'use_ros2_control',
        default_value='false',
        description='Use ros2_control hardware interface'
    )

    # Robot description
    robot_description_content = Command([
        'xacro ',
        os.path.join(bungy_description_dir, 'urdf', 'bungy_robot.urdf.xacro'),
        ' use_ros2_control:=', LaunchConfiguration('use_ros2_control'),
        ' use_sim_time:=', LaunchConfiguration('use_sim_time')
    ])

    robot_description = {'robot_description': robot_description_content}

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            robot_description,
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ]
    )

    return LaunchDescription([
        use_sim_time_arg,
        use_ros2_control_arg,
        robot_state_publisher,
    ])
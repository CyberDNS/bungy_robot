#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    # Package directories
    bungy_description_dir = get_package_share_directory('bungy_description')
    
    # Path to URDF file
    urdf_file = os.path.join(bungy_description_dir, 'urdf', 'bungy_robot.urdf.xacro')
    
    # Process the URDF file
    doc = xacro.process_file(urdf_file)
    robot_description = doc.toprettyxml(indent='  ')
    
    # Launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time'
    )

    # Robot state publisher with bungy namespace
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        namespace='bungy',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'frame_prefix': 'bungy/'
        }],
        output='screen'
    )

    return LaunchDescription([
        use_sim_time_arg,
        robot_state_publisher_node,
    ])
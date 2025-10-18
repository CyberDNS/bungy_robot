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
    
    # Process the URDF file and add bungy namespace to frames
    doc = xacro.process_file(urdf_file)
    robot_description = doc.toprettyxml(indent='  ')
    
    # Add bungy namespace to all frame names
    robot_description = robot_description.replace('name="base_link"', 'name="bungy/base_link"')
    robot_description = robot_description.replace('link="base_link"', 'link="bungy/base_link"')
    robot_description = robot_description.replace('name="left_wheel_link"', 'name="bungy/left_wheel_link"')
    robot_description = robot_description.replace('link="left_wheel_link"', 'link="bungy/left_wheel_link"')
    robot_description = robot_description.replace('name="right_wheel_link"', 'name="bungy/right_wheel_link"')
    robot_description = robot_description.replace('link="right_wheel_link"', 'link="bungy/right_wheel_link"')
    robot_description = robot_description.replace('name="laser_link"', 'name="bungy/laser_link"')
    robot_description = robot_description.replace('link="laser_link"', 'link="bungy/laser_link"')
    
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
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
        remappings=[
            ('/joint_states', '/bungy/joint_states'),
            ('/tf', '/tf'),
            ('/tf_static', '/tf_static')
        ],
        output='screen'
    )

    return LaunchDescription([
        use_sim_time_arg,
        robot_state_publisher_node,
    ])
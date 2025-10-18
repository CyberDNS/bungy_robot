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
        default_value=os.path.join(bungy_monitoring_dir, 'rviz', 'robot_with_lidar.rviz'),
        description='Path to RVIZ config file'
    )

    # Local robot state publisher using visual URDF
    from launch.substitutions import Command, PathJoinSubstitution
    from launch_ros.parameter_descriptions import ParameterValue
    from launch_ros.substitutions import FindPackageShare
    
    # Use monitoring-specific visual URDF
    urdf_path = PathJoinSubstitution([
        FindPackageShare("bungy_monitoring"), "urdf", "bungy_visual.urdf.xacro"
    ])

    robot_description = ParameterValue(
        Command(["xacro", " ", urdf_path]),
        value_type=str
    )

    # Local robot state publisher for visuals
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
        output="screen",
    )

    # Joint state publisher to connect robot joint states to local robot model
    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
        remappings=[("/joint_states", "/bungy/joint_states")],
        output="screen",
    )

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
        robot_state_publisher,
        joint_state_publisher, 
        rviz_node,
    ])
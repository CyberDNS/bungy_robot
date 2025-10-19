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

    # Local robot state publisher for RViz visualization  
    # This publishes to global /robot_description for RViz but doesn't publish TF
    # The robot itself publishes the actual TF transforms in bungy/ namespace
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

    # Local robot state publisher for RViz visuals only - no TF publishing
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="local_robot_state_publisher",
        parameters=[{"robot_description": robot_description, "publish_tf": False}],
        output="screen",
    )

    # Robot is already publishing joint states at /bungy/joint_states and TF transforms
    # We don't need a local robot_state_publisher since we use the robot's namespaced frames directly

    # Static transform to bridge robot's TF tree with our local visual tree
    tf_bridge = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_bridge',
        arguments=['0', '0', '0', '0', '0', '0', 'bungy/base_link', 'base_link'],
        output='screen'
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
        tf_bridge,
        rviz_node,
    ])
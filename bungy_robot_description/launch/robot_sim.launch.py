import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource


from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Declare arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_ros2_control",
            default_value="true",
            description="Use ros2 control. This is useful for Gazebo.",
        )
    )

    description_package = "bungy_robot_description"
    use_ros2_control = LaunchConfiguration("use_ros2_control")

    # Get URDF via xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare(description_package), "urdf", "robot_sim.urdf.xacro"]
            ),
            " ",
            "sim:=",
            "true",
            " ",
            "use_ros2_control:=",
            use_ros2_control,            
        ]
    )
    robot_description = {"robot_description": robot_description_content, 'use_sim_time': True}

    rviz_config_file = PathJoinSubstitution([FindPackageShare(description_package), "rviz", "robot_view.rviz"])

    joint_state_publisher_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
    )
    
    if use_ros2_control:
        diff_cont_spawner = Node(
            package="controller_manager",
            executable="spawner",
            arguments=["diff_cont"],
            condition=IfCondition(use_ros2_control),
        )

        joint_broad_spawner = Node(
            package="controller_manager",
            executable="spawner",
            arguments=["joint_broad"],
            condition=IfCondition(use_ros2_control),
        )


    gazebo_params_file = os.path.join(get_package_share_directory('bungy_robot_description'), 'config', 'gazebo_params.yaml') 
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch'), '/gazebo.launch.py']),
            launch_arguments={'extra_gazebo_args': '--ros-args --params-file' + gazebo_params_file}.items()
        )
    
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'bungy'],
                        output='screen',
                        )

    nodes = [
        #joint_state_publisher_node,
        robot_state_publisher_node,
        #rviz_node,
        spawn_entity,
        gazebo,
        diff_cont_spawner,
        joint_broad_spawner
    ]

    return LaunchDescription(declared_arguments + nodes)

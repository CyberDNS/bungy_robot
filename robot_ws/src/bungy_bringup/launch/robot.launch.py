from launch import LaunchDescription
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Use robot description from core_ws
    urdf_path = PathJoinSubstitution([
        FindPackageShare("bungy_description"), "urdf", "bungy_robot.urdf.xacro"
    ])

    robot_description = ParameterValue(
        Command(["xacro", " ", urdf_path, " use_ros2_control:=true"]),
        value_type=str
    )

    controllers_yaml = PathJoinSubstitution([
        FindPackageShare("bungy_bringup"), "config", "controllers.yaml"
    ])

    # Robot state publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        namespace="bungy",
        parameters=[{"robot_description": robot_description}],
        output="screen",
    )

    # Controller manager
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        name="controller_manager",
        namespace="bungy",
        parameters=[controllers_yaml],
        output="screen",
    )

    # Joint state broadcaster spawner
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/bungy/controller_manager"],
        output="screen",
    )

    # Diff drive controller spawner
    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont", "--controller-manager", "/bungy/controller_manager"],
        output="screen",
    )

    # Twist to stamped relay
    twist_relay = Node(
        package="bungy_bringup",
        executable="twist_to_stamped_relay.py",
        name="twist_to_stamped_relay",
        output="screen",
        parameters=[
            {"input_topic": "/cmd_vel"},
            {"output_topic": "/bungy/diff_cont/cmd_vel"},
            {"frame_id": "base_link"},
        ],
    )

    return LaunchDescription([
        robot_state_publisher,
        controller_manager,
        joint_state_broadcaster_spawner,
        diff_drive_controller_spawner,
        twist_relay,
    ])
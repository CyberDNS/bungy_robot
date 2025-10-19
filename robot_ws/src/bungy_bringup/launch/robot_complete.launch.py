#!/usr/bin/env python3
from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution, Command
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
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
        parameters=[{"robot_description": robot_description, "frame_prefix": "bungy/"}],
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

    # RPLIDAR A1
    lidar_node = Node(
        package="rplidar_ros",
        executable="rplidar_composition",
        name="rplidar_node",
        output="screen",
        parameters=[{
            "serial_port": "/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0",
            "frame_id": "laser_link",
            "angle_compensate": True,
            "scan_frequency": 7.0,
        }],
    )

    # BNO055 IMU
    imu_node = Node(
        package="bno055",
        executable="bno055",
        name="bno055_imu",
        output="screen",
        parameters=[{
            "connection_type": "i2c",
            "i2c_bus": 1,
            "i2c_addr": 40,
            "frame_id": "imu_link",
            "data_query_frequency": 10,
            "calib_status_frequency": 0.1,
            "operation_mode": 8,  # IMU mode (gyro + accel only, no magnetometer)
        }],
    )

    # Joystick configuration
    joystick_config = PathJoinSubstitution([
        FindPackageShare("bungy_bringup"), "config", "joystick.yaml"
    ])

    # EKF configuration
    ekf_config = PathJoinSubstitution([
        FindPackageShare("bungy_bringup"), "config", "ekf.yaml"
    ])

    # Joy node
    joy_node = Node(
        package="joy",
        executable="joy_node",
        name="joy_node",
        parameters=[joystick_config],
        output="screen",
    )

    # Teleop twist joy
    teleop_node = Node(
        package="teleop_twist_joy",
        executable="teleop_node",
        name="teleop_node",
        parameters=[joystick_config],
        output="screen",
    )

    # EKF for sensor fusion (IMU + Wheel odometry)
    ekf_node = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        namespace="bungy",
        output="screen",
        parameters=[ekf_config],
        remappings=[
            ("odometry/filtered", "/bungy/odometry/filtered"),
        ],
    )

    return LaunchDescription([
        robot_state_publisher,
        controller_manager,
        joint_state_broadcaster_spawner,
        diff_drive_controller_spawner,
        twist_relay,
        lidar_node,
        imu_node,
        ekf_node,
        joy_node,
        teleop_node,
    ])
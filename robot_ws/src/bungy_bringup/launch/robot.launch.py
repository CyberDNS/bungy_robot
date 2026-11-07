"""Full bringup of the Bungy robot (runs on the Raspberry Pi).

Starts robot_state_publisher, ros2_control (Dynamixel drive), the cmd_vel relay,
RPLIDAR, BNO055 IMU, the EKF and (optionally) the joystick teleop.

Arguments:
  joystick:=true|false      include joystick teleop (default true)
  dynamixel_port:=<device>  serial device of the Dynamixel USB adapter
  lidar_port:=<device>      serial device of the RPLIDAR
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    joystick = LaunchConfiguration("joystick")
    dynamixel_port = LaunchConfiguration("dynamixel_port")
    lidar_port = LaunchConfiguration("lidar_port")

    arguments = [
        DeclareLaunchArgument(
            "joystick", default_value="true",
            description="Include joystick teleop (joy + teleop_twist_joy)",
        ),
        DeclareLaunchArgument(
            "dynamixel_port",
            default_value="/dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FT78LS5T-if00-port0",
            description="Serial device of the Dynamixel USB adapter",
        ),
        DeclareLaunchArgument(
            "lidar_port",
            default_value="/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0",
            description="Serial device of the RPLIDAR",
        ),
    ]

    # Robot description from core_ws (bungy_description)
    urdf_path = PathJoinSubstitution([
        FindPackageShare("bungy_description"), "urdf", "bungy_robot.urdf.xacro"
    ])
    robot_description = ParameterValue(
        Command(["xacro", " ", urdf_path, " use_ros2_control:=true",
                 " dynamixel_port:=", dynamixel_port]),
        value_type=str,
    )

    controllers_yaml = PathJoinSubstitution([
        FindPackageShare("bungy_bringup"), "config", "controllers.yaml"
    ])
    ekf_config = PathJoinSubstitution([
        FindPackageShare("bungy_bringup"), "config", "ekf.yaml"
    ])

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        namespace="bungy",
        parameters=[{"robot_description": robot_description, "frame_prefix": "bungy/"}],
        remappings=[("joint_states", "/bungy/joint_states")],
        output="screen",
    )

    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        name="controller_manager",
        namespace="bungy",
        parameters=[controllers_yaml],
        output="screen",
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/bungy/controller_manager"],
        output="screen",
    )

    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont", "--controller-manager", "/bungy/controller_manager"],
        output="screen",
    )

    # All velocity sources (joystick, Nav2, test scripts) go through twist_mux, which publishes
    # /cmd_vel. The e-stop lock on /e_stop blocks every input.
    twist_mux = Node(
        package="twist_mux",
        executable="twist_mux",
        name="twist_mux",
        output="screen",
        parameters=[PathJoinSubstitution([FindPackageShare("bungy_bringup"), "config", "twist_mux.yaml"])],
        remappings=[("cmd_vel_out", "/cmd_vel")],
    )

    estop = Node(
        package="bungy_bringup",
        executable="estop_node",
        name="estop",
        output="screen",
    )

    # /cmd_vel (Twist) -> /bungy/diff_cont/cmd_vel (TwistStamped)
    twist_relay = Node(
        package="bungy_bringup",
        executable="twist_to_stamped_relay",
        name="twist_to_stamped_relay",
        output="screen",
        parameters=[
            {"input_topic": "/cmd_vel"},
            {"output_topic": "/bungy/diff_cont/cmd_vel"},
            {"frame_id": "bungy/base_link"},
        ],
    )

    lidar_node = Node(
        package="rplidar_ros",
        executable="rplidar_composition",
        name="rplidar_node",
        output="screen",
        parameters=[{
            "serial_port": lidar_port,
            "frame_id": "bungy/laser_link",
            "angle_compensate": True,
            "scan_frequency": 7.0,
        }],
    )

    imu_node = Node(
        package="bno055",
        executable="bno055",
        name="bno055_imu",
        output="screen",
        parameters=[{
            "connection_type": "i2c",
            "i2c_bus": 1,
            "i2c_addr": 40,
            "frame_id": "bungy/imu_link",
            "data_query_frequency": 10,
            "calib_status_frequency": 0.1,
            "operation_mode": 8,  # IMU mode (gyro + accel only, no magnetometer)
        }],
    )

    # EKF: wheel odometry + IMU yaw -> odom->base_link TF
    ekf_node = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        namespace="bungy",
        output="screen",
        parameters=[ekf_config],
        remappings=[("odometry/filtered", "/bungy/odometry/filtered")],
    )

    joystick_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare("bungy_bringup"), "launch", "joystick.launch.py"])
        ]),
        condition=IfCondition(joystick),
    )

    return LaunchDescription(arguments + [
        robot_state_publisher,
        controller_manager,
        joint_state_broadcaster_spawner,
        diff_drive_controller_spawner,
        twist_mux,
        estop,
        twist_relay,
        lidar_node,
        imu_node,
        ekf_node,
        joystick_launch,
    ])

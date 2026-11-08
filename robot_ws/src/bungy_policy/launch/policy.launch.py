"""Robot bringup + collision monitor + the learned local planner (no Nav2 controller/smoother).

  ros2 launch bungy_policy policy.launch.py [max_speed:=0.1] [goal_topic:=/goal_pose]

The policy publishes /cmd_vel_smoothed, the collision monitor's input; its output /cmd_vel_nav_safe
is the navigation input of twist_mux, so joystick / pause / e-stop keep working exactly as with Nav2.
Goal: a geometry_msgs/PoseStamped on goal_topic (rviz "2D Goal Pose"), in any frame that TF can
transform to bungy/base_link (bungy/odom works without a map; bungy/map needs AMCL running).
Do not run together with navigation.launch.py (both drive the same mux input).
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    policy = FindPackageShare("bungy_policy")
    bringup = FindPackageShare("bungy_bringup")

    args = [
        DeclareLaunchArgument("max_speed", default_value="0.1",
                              description="Cap on |linear.x| in m/s (rollout ladder: 0.1, then 0.3)"),
        DeclareLaunchArgument("goal_topic", default_value="/goal_pose"),
        DeclareLaunchArgument("laser_yaw", default_value="0.0",
                              description="Lidar rotation against base_link in rad: CHECK on the robot"),
        DeclareLaunchArgument("model", default_value=PathJoinSubstitution(
            [policy, "models", "rob-s0", "policy.onnx"])),
    ]

    robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([bringup, "launch", "robot.launch.py"])))

    monitor = Node(package="nav2_collision_monitor", executable="collision_monitor",
                   name="collision_monitor", output="screen",
                   parameters=[PathJoinSubstitution([policy, "config", "collision_monitor.yaml"])])
    lifecycle = Node(package="nav2_lifecycle_manager", executable="lifecycle_manager",
                     name="lifecycle_manager_policy", output="screen",
                     parameters=[{"autostart": True, "bond_timeout": 0.0,
                                  "node_names": ["collision_monitor"]}])

    planner = Node(package="bungy_policy", executable="learned_local_planner",
                   name="learned_local_planner", output="screen",
                   parameters=[{"model": LaunchConfiguration("model"),
                                "max_speed": LaunchConfiguration("max_speed"),
                                "goal_topic": LaunchConfiguration("goal_topic"),
                                "laser_yaw": LaunchConfiguration("laser_yaw")}])

    return LaunchDescription(args + [robot, monitor, lifecycle, planner])

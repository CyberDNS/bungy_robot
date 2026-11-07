"""Robot bringup plus Nav2 (map server, AMCL, planner, controller, behaviours, collision monitor).

  ros2 launch bungy_bringup navigation.launch.py [map:=/home/david/maps/room1.yaml]

Everything runs on the Pi. AMCL needs the initial pose: use "2D Pose Estimate" in rviz (bungy_nav.rviz),
then "2D Goal Pose". Nav2's final command (collision_monitor) goes to /cmd_vel_nav_safe, the navigation
input of twist_mux: B pauses it, the stick overrides it, Menu resumes it.
Do not run it together with mapping.launch.py (both publish the bungy/map -> bungy/odom transform).
"""
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    bringup = FindPackageShare("bungy_bringup")
    params = LaunchConfiguration("params_file")
    map_yaml = LaunchConfiguration("map")

    args = [
        DeclareLaunchArgument("map", default_value=os.path.expanduser("~/maps/room1.yaml"),
                              description="Map yaml (from tools/save_map.sh)"),
        DeclareLaunchArgument("params_file",
                              default_value=PathJoinSubstitution([bringup, "config", "nav2_params.yaml"])),
    ]

    robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([bringup, "launch", "robot.launch.py"])),
    )

    def nav2(package, executable, name, remappings=None, extra=None):
        return Node(
            package=package, executable=executable, name=name, output="screen",
            parameters=[params] + ([extra] if extra else []),
            remappings=remappings or [],
        )

    to_nav = [("cmd_vel", "cmd_vel_nav")]
    localization = [
        nav2("nav2_map_server", "map_server", "map_server", extra={"yaml_filename": map_yaml}),
        nav2("nav2_amcl", "amcl", "amcl"),
        Node(package="nav2_lifecycle_manager", executable="lifecycle_manager",
             name="lifecycle_manager_localization", output="screen",
             parameters=[{"autostart": True, "bond_timeout": 0.0,
                          "node_names": ["map_server", "amcl"]}]),
    ]
    navigation = [
        nav2("nav2_controller", "controller_server", "controller_server", remappings=to_nav),
        nav2("nav2_planner", "planner_server", "planner_server"),
        nav2("nav2_behaviors", "behavior_server", "behavior_server", remappings=to_nav),
        nav2("nav2_bt_navigator", "bt_navigator", "bt_navigator"),
        nav2("nav2_waypoint_follower", "waypoint_follower", "waypoint_follower"),
        nav2("nav2_velocity_smoother", "velocity_smoother", "velocity_smoother", remappings=to_nav),
        nav2("nav2_collision_monitor", "collision_monitor", "collision_monitor"),
        Node(package="nav2_lifecycle_manager", executable="lifecycle_manager",
             name="lifecycle_manager_navigation", output="screen",
             # started by nav2_startup once AMCL has an initial pose (the global costmap needs bungy/map)
             parameters=[{"autostart": False, "bond_timeout": 0.0,
                          "node_names": ["controller_server", "planner_server", "behavior_server",
                                         "bt_navigator", "waypoint_follower", "velocity_smoother",
                                         "collision_monitor"]}]),
    ]

    startup = Node(package="bungy_bringup", executable="nav2_startup", name="nav2_startup", output="screen")

    return LaunchDescription(args + [robot] + localization + navigation + [startup])

"""Robot bringup plus slam_toolbox: drive around (joystick) to build a map.

  ros2 launch bungy_bringup mapping.launch.py

Save the result with tools/save_map.sh NAME (see README, "Mapping").
slam_toolbox is a lifecycle node: it is configured and activated here, like the stock launch file.
"""
from launch import LaunchDescription
from launch.actions import EmitEvent, IncludeLaunchDescription, LogInfo, RegisterEventHandler
from launch.events import matches_action
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from launch_ros.substitutions import FindPackageShare
from lifecycle_msgs.msg import Transition


def generate_launch_description():
    bringup = FindPackageShare("bungy_bringup")

    robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([bringup, "launch", "robot.launch.py"])),
    )

    slam = LifecycleNode(
        package="slam_toolbox",
        executable="async_slam_toolbox_node",
        name="slam_toolbox",
        namespace="",
        output="screen",
        parameters=[
            PathJoinSubstitution([bringup, "config", "slam_toolbox.yaml"]),
            {"use_lifecycle_manager": False, "use_sim_time": False},
        ],
    )

    configure = EmitEvent(event=ChangeState(
        lifecycle_node_matcher=matches_action(slam),
        transition_id=Transition.TRANSITION_CONFIGURE,
    ))

    activate = RegisterEventHandler(OnStateTransition(
        target_lifecycle_node=slam,
        start_state="configuring",
        goal_state="inactive",
        entities=[
            LogInfo(msg="slam_toolbox configured, activating"),
            EmitEvent(event=ChangeState(
                lifecycle_node_matcher=matches_action(slam),
                transition_id=Transition.TRANSITION_ACTIVATE,
            )),
        ],
    ))

    return LaunchDescription([robot, slam, configure, activate])

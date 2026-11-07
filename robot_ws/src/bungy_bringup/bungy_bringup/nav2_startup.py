#!/usr/bin/env python3
"""Starts the Nav2 navigation nodes once the robot is localized.

AMCL publishes bungy/map -> bungy/odom only after it has an initial pose (rviz "2D Pose Estimate").
The global costmap needs that transform to activate and gives up after a minute, which aborts the
whole bring-up. This node waits for the transform and then starts lifecycle_manager_navigation
(launched with autostart: false).
"""
import rclpy
from rclpy.node import Node
from rclpy.time import Time
from nav2_msgs.srv import ManageLifecycleNodes
from tf2_ros import Buffer, TransformListener


class Nav2Startup(Node):
    def __init__(self):
        super().__init__('nav2_startup')
        self.declare_parameter('manager', 'lifecycle_manager_navigation')
        self.declare_parameter('map_frame', 'bungy/map')
        self.declare_parameter('base_frame', 'bungy/base_link')
        self.map_frame = self.get_parameter('map_frame').value
        self.base_frame = self.get_parameter('base_frame').value
        manager = self.get_parameter('manager').value
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.client = self.create_client(ManageLifecycleNodes, f'/{manager}/manage_nodes')
        self.started = False
        self.waited = 0
        self.timer = self.create_timer(1.0, self.tick)
        self.get_logger().info(
            f'waiting for the robot to be localized ({self.map_frame}): set the initial pose in rviz')

    def tick(self):
        if self.started:
            return
        if not self.tf_buffer.can_transform(self.map_frame, self.base_frame, Time()):
            self.waited += 1
            if self.waited % 15 == 0:
                self.get_logger().info('still waiting for the initial pose (rviz: 2D Pose Estimate)')
            return
        if not self.client.service_is_ready():
            return
        self.started = True
        request = ManageLifecycleNodes.Request()
        request.command = ManageLifecycleNodes.Request.STARTUP
        future = self.client.call_async(request)
        future.add_done_callback(self.done)
        self.get_logger().info('localized: starting the navigation nodes')

    def done(self, future):
        ok = future.result() is not None and future.result().success
        self.get_logger().info('navigation nodes active' if ok else 'starting the navigation nodes FAILED')
        self.timer.cancel()


def main():
    rclpy.init()
    node = Nav2Startup()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

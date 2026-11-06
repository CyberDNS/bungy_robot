#!/usr/bin/env python3
"""Drive straight for a short, fixed time and stop.

Usage: ros2 run bungy_bringup drive_straight_test [--ros-args -p speed:=0.2 -p duration:=2.0]
Publishes Twist on /cmd_vel (the twist_to_stamped_relay forwards it to the controller).
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class DriveStraightTest(Node):
    def __init__(self):
        super().__init__('drive_straight_test')
        self.declare_parameter('speed', 0.2)      # m/s
        self.declare_parameter('duration', 2.0)   # s
        self.speed = self.get_parameter('speed').value
        self.duration = self.get_parameter('duration').value

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.start = None
        self.stop_count = 0
        self.done = False
        self.create_timer(0.1, self.tick)  # 10 Hz

    def tick(self):
        now = self.get_clock().now()
        if self.start is None:
            # Wait until the relay is subscribed so the first command isn't lost
            if self.publisher.get_subscription_count() == 0:
                return
            self.start = now
            self.get_logger().info(
                f'Driving straight at {self.speed} m/s for {self.duration} s')

        elapsed = (now - self.start).nanoseconds / 1e9
        msg = Twist()
        if elapsed < self.duration:
            msg.linear.x = self.speed
            self.publisher.publish(msg)
        else:
            # Send several stop commands, then finish
            self.publisher.publish(msg)
            self.stop_count += 1
            if self.stop_count >= 5:
                self.get_logger().info('Drive test completed. Robot stopped.')
                self.done = True


def main(args=None):
    rclpy.init(args=args)
    node = DriveStraightTest()
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        # Always leave the robot stopped
        node.publisher.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

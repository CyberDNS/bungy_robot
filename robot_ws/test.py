#!/usr/bin/env python3
import time
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from geometry_msgs.msg import TwistStamped

TOPIC = '/bungy/diff_cont/cmd_vel'

class TurnTest(Node):
    def __init__(self):
        super().__init__('turn_test')
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=10,
        )
        self.pub = self.create_publisher(TwistStamped, TOPIC, qos)

    def wait_for_sub(self, timeout=5.0):
        start = time.time()
        while rclpy.ok() and time.time() - start < timeout:
            if self.pub.get_subscription_count() > 0:
                return True
            time.sleep(0.05)
        return False

    def turn(self, angular_speed=1.0, duration=3.14, rate_hz=20):
        if not self.wait_for_sub():
            self.get_logger().warn(
                f"No subscriber on {TOPIC} after timeout; publishing anyway (check controller active & topic)")
        msg = TwistStamped()
        msg.header.frame_id = 'base_link'
        period = 1.0 / rate_hz
        end = time.time() + duration

        self.get_logger().info(f"Turning at {angular_speed} rad/s for {duration} s")
        while rclpy.ok() and time.time() < end:
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.twist.angular.z = angular_speed
            self.pub.publish(msg)
            time.sleep(period)

        # stop
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.twist.angular.z = 0.0
        self.pub.publish(msg)
        self.get_logger().info("Stopped.")

def main():
    rclpy.init()
    node = TurnTest()
    try:
        node.turn()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
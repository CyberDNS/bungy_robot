#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped


class TwistToStampedRelay(Node):
    def __init__(self):
        super().__init__("twist_to_stamped_relay")

        # Parameters (for flexibility)
        self.declare_parameter("input_topic", "/cmd_vel")
        self.declare_parameter("output_topic", "/bungy/diff_cont/cmd_vel")
        self.declare_parameter("frame_id", "base_link")

        input_topic = self.get_parameter("input_topic").get_parameter_value().string_value
        output_topic = self.get_parameter("output_topic").get_parameter_value().string_value
        self.frame_id = self.get_parameter("frame_id").get_parameter_value().string_value

        # Publisher and subscriber
        self.publisher_ = self.create_publisher(TwistStamped, output_topic, 10)
        self.subscription = self.create_subscription(Twist, input_topic, self.callback, 10)

        self.get_logger().info(
            f"Relaying {input_topic} (Twist) → {output_topic} (TwistStamped) [frame_id={self.frame_id}]"
        )

    def callback(self, msg: Twist):
        stamped = TwistStamped()
        stamped.header.stamp = self.get_clock().now().to_msg()
        stamped.header.frame_id = self.frame_id
        stamped.twist = msg
        self.publisher_.publish(stamped)


def main(args=None):
    rclpy.init(args=args)
    node = TwistToStampedRelay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

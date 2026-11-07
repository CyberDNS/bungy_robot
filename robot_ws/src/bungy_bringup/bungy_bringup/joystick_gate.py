#!/usr/bin/env python3
"""Lets the joystick take over from autonomous driving only while the stick is used.

teleop_twist_joy publishes a (zero) command continuously while the pad is connected. With twist_mux
those zeros would outrank navigation for ever. This node forwards the commands only while the stick
is deflected, plus `hold_after` seconds of zeros after it is released so the robot stops; then it
goes silent and the mux hands control back to the next input (navigation unless paused).

  /cmd_vel_joy_raw (Twist, from teleop_twist_joy)  ->  /cmd_vel_joy (Twist, into twist_mux)
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class JoystickGate(Node):
    def __init__(self):
        super().__init__('joystick_gate')
        self.declare_parameter('hold_after', 0.3)
        self.hold_after = self.get_parameter('hold_after').value
        self.last_active = None
        self.pub = self.create_publisher(Twist, '/cmd_vel_joy', 10)
        self.create_subscription(Twist, '/cmd_vel_joy_raw', self.on_cmd, 10)

    def on_cmd(self, msg):
        now = self.get_clock().now()
        active = any(abs(v) > 1e-6 for v in (msg.linear.x, msg.linear.y, msg.linear.z,
                                             msg.angular.x, msg.angular.y, msg.angular.z))
        if active:
            self.last_active = now
            self.pub.publish(msg)
        elif self.last_active is not None and \
                (now - self.last_active).nanoseconds * 1e-9 < self.hold_after:
            self.pub.publish(msg)  # zeros: stop the robot after the stick was released


def main():
    rclpy.init()
    node = JoystickGate()
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

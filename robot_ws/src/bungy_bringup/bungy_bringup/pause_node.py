#!/usr/bin/env python3
"""Pause / resume button for autonomous driving.

Publishes std_msgs/Bool on /pause_navigation (latched). twist_mux uses it as a lock with a priority
between the autonomous inputs and the joystick: while True, navigation and test-script commands are
blocked and the joystick still works, so the robot can be driven by hand to a safe place.

  pause_button   (default 1, B on an Xbox pad)    -> paused  (/pause_navigation = True)
  resume_button  (default 7, Menu on an Xbox pad) -> resumed (/pause_navigation = False)

Anything else may publish on /pause_navigation too; the lock follows the latest message.
The robot starts resumed. (The hard stop that blocks every input is the separate /e_stop lock.)
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from sensor_msgs.msg import Joy
from std_msgs.msg import Bool


class Pause(Node):
    def __init__(self):
        super().__init__('pause')
        self.declare_parameter('pause_button', 1)
        self.declare_parameter('resume_button', 7)
        self.pause_button = self.get_parameter('pause_button').value
        self.resume_button = self.get_parameter('resume_button').value
        qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                         durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.pub = self.create_publisher(Bool, '/pause_navigation', qos)
        self.create_subscription(Joy, '/joy', self.on_joy, 10)
        self.prev = []
        self.set(False, 'started')

    def set(self, paused, why):
        msg = Bool()
        msg.data = paused
        self.pub.publish(msg)
        self.get_logger().warn(f"autonomous driving {'PAUSED' if paused else 'resumed'} ({why})")

    def pressed(self, buttons, i):
        was = self.prev[i] if i < len(self.prev) else 0
        return i < len(buttons) and buttons[i] == 1 and was == 0

    def on_joy(self, msg):
        if self.pressed(msg.buttons, self.pause_button):
            self.set(True, 'button')
        elif self.pressed(msg.buttons, self.resume_button):
            self.set(False, 'button')
        self.prev = list(msg.buttons)


def main():
    rclpy.init()
    node = Pause()
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

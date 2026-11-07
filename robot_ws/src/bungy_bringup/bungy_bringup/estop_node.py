#!/usr/bin/env python3
"""Emergency-stop button for the command mux.

Publishes std_msgs/Bool on /e_stop (latched). twist_mux uses it as a lock: while True, every
velocity input is blocked and the output is zero.

  engage_button   (default 1, B on an Xbox pad)    -> /e_stop = True
  release_button  (default 7, Menu on an Xbox pad) -> /e_stop = False

Anything else may publish on /e_stop as well (e.g. a navigation watchdog or
`ros2 topic pub --once /e_stop std_msgs/Bool "{data: true}"`); the lock follows the latest message.
The robot starts released.
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from sensor_msgs.msg import Joy
from std_msgs.msg import Bool


class EStop(Node):
    def __init__(self):
        super().__init__('estop')
        self.declare_parameter('engage_button', 1)
        self.declare_parameter('release_button', 7)
        self.engage = self.get_parameter('engage_button').value
        self.release = self.get_parameter('release_button').value
        qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                         durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.pub = self.create_publisher(Bool, '/e_stop', qos)
        self.create_subscription(Joy, '/joy', self.on_joy, 10)
        self.prev = []
        self.set(False, 'started')

    def set(self, value, why):
        msg = Bool()
        msg.data = value
        self.pub.publish(msg)
        self.get_logger().warn(f"E-STOP {'ENGAGED' if value else 'released'} ({why})")

    def pressed(self, buttons, i):
        was = self.prev[i] if i < len(self.prev) else 0
        return i < len(buttons) and buttons[i] == 1 and was == 0

    def on_joy(self, msg):
        if self.pressed(msg.buttons, self.engage):
            self.set(True, 'button')
        elif self.pressed(msg.buttons, self.release):
            self.set(False, 'button')
        self.prev = list(msg.buttons)


def main():
    rclpy.init()
    node = EStop()
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

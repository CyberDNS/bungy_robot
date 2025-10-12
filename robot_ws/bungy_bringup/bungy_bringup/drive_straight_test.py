#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time


class DriveStraightTest(Node):
    def __init__(self):
        super().__init__('drive_straight_test')
        
        # Publisher to send velocity commands
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Wait a moment for publisher to be ready
        time.sleep(0.5)
        
        self.get_logger().info('Starting 2-second straight drive test...')
        
        # Create velocity message
        twist_msg = Twist()
        twist_msg.linear.x = 0.2  # 0.2 m/s forward
        twist_msg.linear.y = 0.0
        twist_msg.linear.z = 0.0
        twist_msg.angular.x = 0.0
        twist_msg.angular.y = 0.0
        twist_msg.angular.z = 0.0  # No rotation
        
        # Publish velocity commands for 2 seconds
        start_time = time.time()
        rate = self.create_rate(10)  # 10 Hz
        
        while time.time() - start_time < 2.0:
            self.publisher.publish(twist_msg)
            self.get_logger().info(f'Driving straight... {time.time() - start_time:.1f}s')
            rate.sleep()
        
        # Stop the robot
        stop_msg = Twist()  # All zeros
        for _ in range(5):  # Send stop command multiple times
            self.publisher.publish(stop_msg)
            time.sleep(0.1)
        
        self.get_logger().info('Drive test completed. Robot stopped.')


def main(args=None):
    rclpy.init(args=args)
    
    node = DriveStraightTest()
    
    # Keep node alive briefly to ensure stop commands are sent
    rclpy.spin_once(node, timeout_sec=1.0)
    
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
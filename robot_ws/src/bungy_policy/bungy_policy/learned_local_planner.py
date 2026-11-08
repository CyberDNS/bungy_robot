#!/usr/bin/env python3
"""Learned local planner: runs the ONNX policy of bungy_robot_rl at 10 Hz.

  /scan, goal (PoseStamped, via TF), /bungy/odometry/filtered
      -> bin_scan + make_observation (interface.py, copied unchanged from bungy_robot_rl)
      -> ONNX actor -> action_to_twist -> speed cap -> /cmd_vel_smoothed (collision monitor input)

Safety behaviour: stale scan/odometry/TF or no goal -> zero Twist. Goal reached -> zero Twist and the
goal is dropped. No progress for `stall_timeout` s -> zero Twist, goal dropped (the policy has no
memory and can deadlock behind a box). Every command the collision monitor changes is counted and
logged, so the policy's own behaviour can be told apart from the monitor's rescues.

See bungy_robot_rl/docs/deployment.md for the contract and the checks to run on the robot.
"""
import math
import os
import sys
import time

import numpy as np
import rclpy
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from tf2_ros import Buffer, TransformException, TransformListener

from bungy_policy.interface import action_to_twist, bin_scan, make_observation


def import_onnxruntime(extra_path):
    """onnxruntime is not installable system-wide on the Pi (no pip, PEP 668): it is unpacked to a folder."""
    try:
        import onnxruntime
        return onnxruntime
    except ImportError:
        path = os.path.expanduser(extra_path)
        if not os.path.isdir(path):
            raise
        sys.path.insert(0, path)
        import onnxruntime
        return onnxruntime


def mark_blind_runs(ranges, near=0.3, range_min=0.15):
    """The RPLIDAR reports objects closer than its minimum range as +inf, not as a small value
    (measured with a hand in front of it). The policy would read that as "nothing there".
    A run of inf/NaN with a close reading (< ``near`` m) on BOTH sides is an object we cannot
    measure, so it becomes ``range_min``; a run next to something far is real open space and stays.
    The scan is circular. Returns a new array.
    """
    r = np.array(ranges, dtype=np.float64)
    bad = ~np.isfinite(r) & ~np.isneginf(r)
    n = len(r)
    if not bad.any() or bad.all():
        return r
    start = int(np.argmin(bad))  # a valid sample, so runs never straddle the array end
    order = (np.arange(n) + start) % n
    i = 0
    while i < n:
        if not bad[order[i]]:
            i += 1
            continue
        j = i
        while j + 1 < n and bad[order[j + 1]]:
            j += 1
        before, after = r[order[i - 1]], r[order[(j + 1) % n]]
        if before < near and after < near:
            r[order[i:j + 1]] = range_min
        i = j + 1
    return r


class LearnedLocalPlanner(Node):
    def __init__(self):
        super().__init__('learned_local_planner')
        p = self.declare_parameter
        p('model', 'policy.onnx')
        p('ort_path', '~/ortlib')
        p('goal_topic', '/goal_pose')
        p('scan_topic', '/scan')
        p('odom_topic', '/bungy/odometry/filtered')
        p('cmd_topic', '/cmd_vel_smoothed')
        p('safe_cmd_topic', '/cmd_vel_nav_safe')
        p('base_frame', 'bungy/base_link')
        p('laser_yaw', 0.0)        # rad, lidar rotation against base_link (deployment.md check 1)
        p('max_speed', 0.1)        # m/s cap on |linear.x|; the policy was trained up to 0.3
        p('max_age', 0.3)          # s, scan / odometry older than this -> stop
        p('goal_tolerance', 0.15)  # m, same as the training success radius
        p('stall_timeout', 8.0)    # s without `stall_progress` m of progress -> give up
        p('stall_progress', 0.10)  # m
        g = lambda n: self.get_parameter(n).value
        self.laser_yaw, self.max_speed, self.max_age = g('laser_yaw'), g('max_speed'), g('max_age')
        self.tol, self.stall_timeout, self.stall_progress = g('goal_tolerance'), g('stall_timeout'), g('stall_progress')
        self.base_frame = g('base_frame')

        ort = import_onnxruntime(g('ort_path'))
        self.sess = ort.InferenceSession(g('model'), providers=['CPUExecutionProvider'])

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.scan, self.scan_rx = None, 0.0
        self.odom, self.odom_rx = None, 0.0
        self.goal = None
        self.best_dist, self.best_time = math.inf, 0.0
        self.sent, self.changed = 0, 0
        self.last_cmd = Twist()

        self.create_subscription(LaserScan, g('scan_topic'), self.on_scan, qos_profile_sensor_data)
        self.create_subscription(Odometry, g('odom_topic'), self.on_odom, qos_profile_sensor_data)
        self.create_subscription(PoseStamped, g('goal_topic'), self.on_goal, 1)
        self.create_subscription(Twist, g('safe_cmd_topic'), self.on_safe, 1)
        self.pub = self.create_publisher(Twist, g('cmd_topic'), 1)
        self.create_timer(0.1, self.tick)  # 10 Hz, as in training
        self.create_timer(10.0, self.report)
        self.get_logger().info(f"policy {g('model')}, speed cap {self.max_speed} m/s, laser_yaw {self.laser_yaw} rad")

    # -- inputs ------------------------------------------------------------------------
    def on_scan(self, msg):
        self.scan, self.scan_rx = msg, time.monotonic()

    def on_odom(self, msg):
        self.odom, self.odom_rx = msg, time.monotonic()

    def on_goal(self, msg):
        self.goal, self.best_dist, self.best_time = msg, math.inf, time.monotonic()
        self.get_logger().info(f'new goal in {msg.header.frame_id}: ({msg.pose.position.x:.2f}, {msg.pose.position.y:.2f})')

    def on_safe(self, msg):
        """Collision monitor output: compare with what we sent."""
        a, b = self.last_cmd, msg
        if abs(a.linear.x - b.linear.x) > 1e-3 or abs(a.angular.z - b.angular.z) > 1e-3:
            self.changed += 1

    def goal_in_base(self):
        pose = PoseStamped()
        pose.header.frame_id = self.goal.header.frame_id
        pose.pose = self.goal.pose  # stamp 0 = latest transform
        try:
            tf = self.tf_buffer.lookup_transform(self.base_frame, pose.header.frame_id, rclpy.time.Time(),
                                                 timeout=Duration(seconds=0.05))
        except TransformException as e:
            self.get_logger().warn(f'no transform to {self.base_frame}: {e}', throttle_duration_sec=2.0)
            return None
        t, q, pos = tf.transform.translation, tf.transform.rotation, self.goal.pose.position
        # rotate the goal position by q and add the translation (planar: yaw only)
        yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
        c, s = math.cos(yaw), math.sin(yaw)
        return c * pos.x - s * pos.y + t.x, s * pos.x + c * pos.y + t.y

    # -- control loop ------------------------------------------------------------------
    def stop(self):
        self.last_cmd = Twist()
        self.pub.publish(self.last_cmd)

    def tick(self):
        now = time.monotonic()
        if self.goal is None:
            return self.stop()
        if self.scan is None or self.odom is None or now - self.scan_rx > self.max_age or now - self.odom_rx > self.max_age:
            self.get_logger().warn('stale scan/odometry: stopping', throttle_duration_sec=2.0)
            return self.stop()
        goal = self.goal_in_base()
        if goal is None:
            return self.stop()
        gx, gy = goal
        dist = math.hypot(gx, gy)
        if dist < self.tol:
            self.get_logger().info(f'goal reached (distance {dist:.2f} m)')
            self.goal = None
            return self.stop()
        if dist < self.best_dist - self.stall_progress:
            self.best_dist, self.best_time = dist, now
        elif now - self.best_time > self.stall_timeout:
            self.get_logger().warn(f'no progress for {self.stall_timeout:.0f} s at {dist:.2f} m from the goal: giving up')
            self.goal = None
            return self.stop()

        s = self.scan
        angles = s.angle_min + np.arange(len(s.ranges)) * s.angle_increment
        bins = bin_scan(angles, mark_blind_runs(s.ranges), yaw_offset=self.laser_yaw)
        tw = self.odom.twist.twist
        obs = make_observation(bins, (gx, gy), tw.linear.x, tw.angular.z)
        action = self.sess.run(None, {'obs': obs[None]})[0][0]
        v, w = action_to_twist(action)
        v = float(np.clip(v, -self.max_speed, self.max_speed))
        msg = Twist()
        msg.linear.x, msg.angular.z = v, w
        self.last_cmd = msg
        self.pub.publish(msg)
        self.sent += 1

    def report(self):
        if self.sent:
            self.get_logger().info(f'collision monitor changed {self.changed} of {self.sent} commands so far')


def main():
    rclpy.init()
    node = LearnedLocalPlanner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.stop()
        except Exception:
            pass
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

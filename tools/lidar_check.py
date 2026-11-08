#!/usr/bin/env python3
"""Lidar checks for the learned policy (bungy_robot_rl/docs/deployment.md, section 5, checks 1 and 3).

  python3 tools/lidar_check.py            # live, refreshes every second, Ctrl-C to stop

Shows the scan header, how many readings are inf / NaN / 0 / below the 0.15 m minimum range, and the
36 policy sectors (10 degrees each, sector 0 = straight ahead, counter-clockwise) as a bar per sector
with the closest sector marked. Sector numbering is computed by the very same bin_scan the policy uses.
Run it on the Pi with the robot bringup running (ros2 launch bungy_bringup robot.launch.py).
"""
import os
import sys

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'robot_ws', 'src', 'bungy_policy'))
from bungy_policy.interface import bin_scan, N_RAYS, LIDAR_MIN_RANGE  # noqa: E402


class Check(Node):
    def __init__(self):
        super().__init__('lidar_check')
        self.msg = None
        self.create_subscription(LaserScan, '/scan', lambda m: setattr(self, 'msg', m), qos_profile_sensor_data)
        self.create_timer(1.0, self.show)

    def show(self):
        s = self.msg
        if s is None:
            print('no /scan yet')
            return
        r = np.asarray(s.ranges, dtype=float)
        ang = s.angle_min + np.arange(len(r)) * s.angle_increment
        bins = bin_scan(ang, r)
        near = int(np.argmin(bins))
        print('\033[2J\033[H', end='')
        print(f'frame_id {s.header.frame_id}  n={len(r)}  angle_min {s.angle_min:.3f}  angle_max {s.angle_max:.3f}  '
              f'incr {s.angle_increment:.4f}  range_min {s.range_min}  range_max {s.range_max}')
        print(f'readings: inf {int(np.isposinf(r).sum())}  -inf {int(np.isneginf(r).sum())}  nan {int(np.isnan(r).sum())}  '
              f'zero {int((r == 0).sum())}  below {LIDAR_MIN_RANGE} m {int(((r > 0) & (r < LIDAR_MIN_RANGE)).sum())}')
        print('\nsector  centre   closest  (sector 0 must be straight ahead, +10 deg per sector, counter-clockwise)')
        for i in range(N_RAYS):
            deg = i * 10 + 5 if i * 10 + 5 <= 180 else i * 10 + 5 - 360
            bar = '#' * int(min(bins[i], 4.0) / 4.0 * 40)
            print(f'{i:5d} {deg:+5d}\N{DEGREE SIGN} {bins[i]:6.2f} m {bar}{"  <== closest" if i == near else ""}')


def main():
    rclpy.init()
    try:
        rclpy.spin(Check())
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()

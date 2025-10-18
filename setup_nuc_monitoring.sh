#!/bin/bash

# NUC Monitoring Setup Script for Bungy Robot
# This script helps set up the monitoring system on the NUC

echo "=== Bungy Robot NUC Monitoring Setup ==="
echo ""

# Set ROS Domain ID for multi-machine communication
export ROS_DOMAIN_ID=42
echo "✓ Set ROS_DOMAIN_ID=42"

# Robot IP (update this to match your robot's actual IP)
ROBOT_IP="192.168.3.110"
echo "✓ Robot IP: $ROBOT_IP"

echo ""
echo "=== Checking Network Connection ==="

# Test network connectivity to robot
if ping -c 1 -W 3 $ROBOT_IP > /dev/null 2>&1; then
    echo "✓ Robot is reachable at $ROBOT_IP"
else
    echo "❌ Cannot reach robot at $ROBOT_IP"
    echo "   Please check:"
    echo "   1. Robot is powered on and connected to network"
    echo "   2. Robot IP is correct"
    echo "   3. Both devices are on same network"
    exit 1
fi

echo ""
echo "=== Checking ROS 2 Topics ==="

# Check if we can see robot topics
echo "Waiting for robot topics..."
timeout 10s bash -c '
while ! ros2 topic list | grep -q "/bungy"; do
    echo "  Waiting for robot topics..."
    sleep 2
done
echo "✓ Robot topics detected!"
'

if [ $? -eq 0 ]; then
    echo ""
    echo "Available robot topics:"
    ros2 topic list | grep "/bungy" | head -10
    echo ""
    echo "=== Ready to Launch Monitoring ==="
    echo ""
    echo "To start monitoring, run:"
    echo "  cd /home/\$USER/bungy_robot/monitoring_ws"
    echo "  source setup.bash"
    echo "  ros2 launch bungy_monitoring remote_monitor.launch.py robot_ip:=$ROBOT_IP"
    echo ""
else
    echo "❌ No robot topics found"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Ensure robot is running: ros2 launch bungy_bringup robot_with_joystick.launch.py"
    echo "2. Check ROS_DOMAIN_ID=42 is set on both robot and NUC"
    echo "3. Verify network connectivity"
    echo "4. Check firewall settings"
    echo ""
    echo "Robot should publish topics like:"
    echo "  /bungy/cmd_vel"
    echo "  /bungy/joint_states"
    echo "  /bungy/robot_description"
fi
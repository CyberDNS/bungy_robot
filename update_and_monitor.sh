#!/bin/bash

# Bungy Robot - Update and Monitor Script
# This script pulls the latest code, builds necessary workspaces, and launches monitoring
# Perfect for quickly getting the latest version running on the NUC

set -e  # Exit on any error

echo "🚀 Bungy Robot - Update and Monitor Script"
echo "=========================================="

# Check if we're in the right directory
if [ ! -d "monitoring_ws" ] || [ ! -d "core_ws" ]; then
    echo "❌ Error: Please run this script from the bungy_robot root directory"
    echo "   Expected directories: monitoring_ws, core_ws"
    echo "   Current directory: $(pwd)"
    exit 1
fi

echo "📥 Pulling latest changes from git..."
git pull

echo "🔧 Building core workspace..."
cd core_ws
colcon build
cd ..

echo "🖥️  Building monitoring workspace..."
cd monitoring_ws
colcon build --packages-select bungy_monitoring
echo "✅ Monitoring workspace built successfully"

echo "🌐 Setting up ROS environment..."
source setup.bash
export ROS_DOMAIN_ID=42

echo "🎯 Launching robot monitoring..."
echo "   - RViz will open with EKF sensor fusion"
echo "   - LIDAR visualization with smaller dots"
echo "   - Green arrows show stable odometry path"
echo ""
echo "💡 Make sure the robot is running on the Raspberry Pi!"
echo "   Robot command: ros2 launch bungy_bringup robot_complete.launch.py"
echo ""

# Launch monitoring with a small delay to ensure messages are ready
sleep 2
ros2 launch bungy_monitoring monitor_robot.launch.py
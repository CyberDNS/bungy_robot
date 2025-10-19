#!/bin/bash

# Bungy Robot - Update and Launch Robot Script
# This script pulls the latest code, builds robot workspace, and launches the robot
# Perfect for quickly getting the latest version running on the Raspberry Pi

set -e  # Exit on any error

echo "🤖 Bungy Robot - Update and Launch Script"
echo "========================================="

# Check if we're in the right directory
if [ ! -d "robot_ws" ] || [ ! -d "core_ws" ]; then
    echo "❌ Error: Please run this script from the bungy_robot root directory"
    echo "   Expected directories: robot_ws, core_ws"
    echo "   Current directory: $(pwd)"
    exit 1
fi

echo "📥 Pulling latest changes from git..."
git pull

echo "🔧 Building core workspace..."
cd core_ws
colcon build
cd ..

echo "🤖 Building robot workspace..."
cd robot_ws
colcon build --packages-select bungy_bringup
echo "✅ Robot workspace built successfully"

echo "🌐 Setting up ROS environment..."
source setup.bash
export ROS_DOMAIN_ID=42

echo "🚀 Launching robot with all sensors..."
echo "   - Dynamixel motors"
echo "   - RPLIDAR A1"
echo "   - BNO055 IMU"
echo "   - EKF sensor fusion"
echo "   - Xbox controller support"
echo ""

# Launch robot system
ros2 launch bungy_bringup robot_complete.launch.py
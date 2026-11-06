#!/bin/bash

# Source ROS2 Jazzy environment
source /opt/ros/jazzy/setup.bash

# Source core workspace for shared robot description
source ../core_ws/install/setup.bash

# Source local monitoring workspace install
source install/setup.bash

# Set ROS_DOMAIN_ID for multi-machine communication
# Both robot and monitoring PC should use the same domain ID
export ROS_DOMAIN_ID=42

# Machine-specific settings (ROBOT_IP) come from the git-ignored bungy.env.local
BUNGY_ENV="$(dirname "${BASH_SOURCE[0]}")/../bungy.env.local"
if [ -f "$BUNGY_ENV" ]; then
    set -a; source "$BUNGY_ENV"; set +a
else
    echo "WARNING: bungy.env.local not found. Run: cp bungy.env.example bungy.env.local"
fi

# Optional: Set specific network interface if needed
# export ROS_LOCALHOST_ONLY=0
# export CYCLONE_DDS_ENABLE_LOCALHOST_ONLY=false

echo "Bungy Robot monitoring workspace setup complete!"
echo "ROS_DOMAIN_ID set to: $ROS_DOMAIN_ID"
echo "Robot IP set to: $ROBOT_IP"
echo ""
echo "To monitor the robot, run:"
echo "  ros2 launch bungy_monitoring monitor_robot.launch.py"
echo ""
echo "For remote control and monitoring, run:"
echo "  ros2 launch bungy_monitoring remote_monitor.launch.py robot_ip:=$ROBOT_IP"
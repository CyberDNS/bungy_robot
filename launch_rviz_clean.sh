#!/bin/bash

# Clean RVIZ2 Launcher - Avoids VS Code snap conflicts
# Usage: ./launch_rviz_clean.sh

echo "=== Clean RVIZ2 Launcher ==="
echo "Cleaning snap environment conflicts..."

# Clean environment variables that snap contaminated
unset LD_LIBRARY_PATH
unset SNAP
unset SNAP_DATA
unset SNAP_COMMON
unset SNAP_USER_DATA
unset SNAP_USER_COMMON

# Set clean library path
export LD_LIBRARY_PATH="/opt/ros/jazzy/lib:/usr/lib/x86_64-linux-gnu:/lib/x86_64-linux-gnu"

# Source ROS environment
source /opt/ros/jazzy/setup.bash

# Navigate to monitoring workspace
cd /home/david/repos/bungy_robot/monitoring_ws
source setup.bash

echo "Launching RVIZ2 with clean environment..."
rviz2 "$@"
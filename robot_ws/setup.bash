#!/bin/bash
# Robot workspace setup -- runs on the Raspberry Pi 4.

# Source ROS2 Jazzy environment
source /opt/ros/jazzy/setup.bash

# Source core workspace for shared robot description
source ../core_ws/install/setup.bash

# Source local workspace install
source install/setup.bash

# Optional machine-specific settings from the git-ignored bungy.env.local
BUNGY_ENV="$(dirname "${BASH_SOURCE[0]}")/../bungy.env.local"
[ -f "$BUNGY_ENV" ] && { set -a; source "$BUNGY_ENV"; set +a; }

# Dynamixel ros2_control hardware driver (separate repo, built on the Pi).
# Override the location via DYNAMIXEL_WS in bungy.env.local
DYNAMIXEL_WS="${DYNAMIXEL_WS:-$HOME/repos/ros2_control_dynamixel_ax12a}"
if [ -f "$DYNAMIXEL_WS/install/setup.bash" ]; then
    source "$DYNAMIXEL_WS/install/setup.bash"
else
    echo "WARNING: Dynamixel driver workspace not found at $DYNAMIXEL_WS (set DYNAMIXEL_WS)"
fi

# Must match the dev machine (NUC)
export ROS_DOMAIN_ID=42

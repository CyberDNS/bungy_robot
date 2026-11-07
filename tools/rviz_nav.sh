#!/bin/bash
# On the NUC: rviz with the navigation view (map, costmaps, plans, particles, goal tools).
#   tools/rviz_nav.sh          (rviz.sh-style: pass rviz_config:=... to use another view)
cd "$(dirname "$0")/../monitoring_ws" || exit 1
source ./setup.bash >/dev/null
exec ros2 launch bungy_monitoring monitor_robot.launch.py \
    rviz_config:="$(ros2 pkg prefix bungy_monitoring)/share/bungy_monitoring/rviz/bungy_nav.rviz" "$@"

#!/bin/bash
# Saves the map slam_toolbox is currently building (run it on the Pi while mapping.launch.py runs).
#   tools/save_map.sh NAME     ->  ~/maps/NAME.yaml + .pgm (for Nav2) and NAME.posegraph + .data
#                                  (slam_toolbox, to continue or localize later)
set -e
name=${1:?usage: save_map.sh NAME}
dir=${MAP_DIR:-$HOME/maps}
mkdir -p "$dir"
source "$(dirname "$0")/../robot_ws/setup.bash" >/dev/null 2>&1
ros2 run nav2_map_server map_saver_cli -f "$dir/$name" --ros-args -p map_subscribe_transient_local:=true
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '$dir/$name'}"
echo "saved to $dir/$name.*"

# bungy_policy

Runs the ONNX policy trained in `bungy_robot_rl` (`policies/rob-s0`) as a local planner, replacing
Nav2's controller and smoother. Contract and background: `bungy_robot_rl/docs/deployment.md`.

Files copied from `bungy_robot_rl` (keep in sync, compare hashes when the model changes):
`bungy_policy/interface.py` (from `src/bungy_rl/envs/interface.py`, do not edit),
`models/rob-s0/policy.onnx` and `policy.json` (from `policies/rob-s0/`, the JSON names the source commit).

## onnxruntime on the Pi

The Pi has no pip and no `python3-venv`, so onnxruntime is unpacked into `~/ortlib` (the node adds it
to `sys.path`, parameter `ort_path`). From the NUC:

    pip download --no-deps --only-binary=:all: --platform manylinux_2_28_aarch64 --python-version 3.12 onnxruntime
    unzip onnxruntime-*.whl -d ortlib && rsync -a ortlib/ bungy:ortlib/

Measured on the Pi 4: onnxruntime 1.31.1, 0.075 ms per inference (budget 100 ms).

## Run

    ./deploy.sh --build            # on the NUC
    ros2 launch bungy_policy policy.launch.py max_speed:=0.1   # on the Pi
    # rviz "2D Goal Pose" (frame bungy/odom works without a map)

Output goes to `/cmd_vel_smoothed` -> collision monitor -> `/cmd_vel_nav_safe` -> twist_mux, so
joystick, pause and e-stop work as with Nav2. Do not run together with `navigation.launch.py`.
The node logs how many commands the collision monitor changed.

## Before the first run

Work through section 5 of `deployment.md`, above all `laser_yaw` (lidar angle convention) and what the
driver publishes for too-close readings. Then the rollout ladder (section 6): stand, 0.1 m/s, 0.3 m/s,
one obstacle, several, side by side with Nav2.

## Robot geometry

Measured values (STL and tape, found in `bungy_robot_rl`) now in the URDF: lidar x = -0.068875 m (it
was +0.08, the wrong sign: AMCL, SLAM and costmaps use it) and the chassis box of 0.192 x 0.194 m, which
reaches 0.128 m behind the axle and only 0.064 m in front. The collision monitor footprint follows that
outline. Nav2's `robot_radius` 0.17 m is conservative (farthest point 0.150 m). Not yet checked: the
lidar mounting yaw (`laser_yaw`, launch argument, default 0), mass and centre of mass, motor lag. The
lidar z (0.09) was left alone: the simulator's 0.133 is measured from another origin.

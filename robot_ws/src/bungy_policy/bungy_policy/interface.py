"""The robot-facing interface of the policy: everything that must be IDENTICAL in simulation
and on the real robot. Pure numpy, no MuJoCo and no ROS, so a ROS node can import it as is.

Why one shared module: the commonest sim-to-real failure is not the physics but a mismatch in
the inputs, such as a different ray order, other units, or invalid lidar readings handled
differently. The environment builds its observation through these very functions, so what the
policy saw in training is by construction what the deployment code feeds it.

Conventions (robot frame = base_link): x forward, y left, angles counter-clockwise from x.
"""

import numpy as np

# ---- action ---------------------------------------------------------------------------
# From nav2_params.yaml of the real robot (velocity limits).
V_MAX, V_MIN, W_MAX = 0.3, -0.15, 1.0  # m/s forward, m/s reverse, rad/s

# ---- observation ----------------------------------------------------------------------
N_RAYS = 36  # lidar sectors of 10 degrees
LIDAR_OBS_RANGE = 4.0  # m; ranges are divided by this and clipped to 1
LIDAR_MIN_RANGE = 0.15  # m, RPLIDAR A1
LIDAR_MAX_RANGE = 12.0  # m
GOAL_SCALE = 4.0 * np.sqrt(2.0)  # m; goal distance is divided by this (diagonal of the 4 m room)
OBS_DIM = N_RAYS + 5


def bin_scan(
    angles: np.ndarray,
    ranges: np.ndarray,
    n_rays: int = N_RAYS,
    range_min: float = LIDAR_MIN_RANGE,
    range_max: float = LIDAR_MAX_RANGE,
    yaw_offset: float = 0.0,
) -> np.ndarray:
    """Reduce a lidar scan to ``n_rays`` sectors holding the closest return (metres).

    ``angles`` are in radians, counter-clockwise from straight ahead, in any range and any
    order (a ROS LaserScan has angle_min + i * angle_increment, often -pi..pi). If the lidar is
    mounted rotated against the robot, pass that rotation as ``yaw_offset``.

    Invalid readings follow REP-117: +inf and NaN mean "nothing in range" and become
    ``range_max``; -inf and values <= 0 mean "closer than the minimum range" and become
    ``range_min`` (the pessimistic choice). A sector without any sample reads ``range_max``.
    """
    angles = np.asarray(angles, dtype=np.float64) + yaw_offset
    ranges = np.asarray(ranges, dtype=np.float64)
    r = np.where(np.isfinite(ranges), ranges, range_max)
    r = np.where(ranges <= 0.0, range_min, r)
    r = np.clip(r, range_min, range_max)
    width = 2 * np.pi / n_rays
    idx = np.floor(np.mod(angles, 2 * np.pi) / width + 1e-9).astype(int) % n_rays
    out = np.full(n_rays, range_max)
    np.minimum.at(out, idx, r)
    return out


def goal_to_robot_frame(goal_xy, x: float, y: float, yaw: float) -> tuple[float, float]:
    """Goal given in some world frame -> (forward, left) offset in the robot frame."""
    dx, dy = goal_xy[0] - x, goal_xy[1] - y
    return (
        float(np.cos(yaw) * dx + np.sin(yaw) * dy),
        float(-np.sin(yaw) * dx + np.cos(yaw) * dy),
    )


def make_observation(
    bins: np.ndarray,
    goal_robot: tuple[float, float],
    v: float,
    omega: float,
    goal_scale: float = GOAL_SCALE,
) -> np.ndarray:
    """Assemble the 41 floats the policy sees.

    ``bins``: output of ``bin_scan`` (metres). ``goal_robot``: (forward, left) offset to the goal
    in metres. ``v``, ``omega``: measured forward speed (m/s) and yaw rate (rad/s).
    """
    gx, gy = goal_robot
    bearing = np.arctan2(gy, gx)
    obs = np.concatenate(
        [
            np.clip(np.asarray(bins) / LIDAR_OBS_RANGE, 0.0, 1.0),
            [min(np.hypot(gx, gy) / goal_scale, 1.0), np.cos(bearing), np.sin(bearing)],
            [np.clip(v / V_MAX, -1.0, 1.0), np.clip(omega / W_MAX, -1.0, 1.0)],
        ]
    )
    return obs.astype(np.float32)


def action_to_twist(action) -> tuple[float, float]:
    """Policy output in [-1, 1]^2 -> (linear.x in m/s, angular.z in rad/s)."""
    a = np.clip(np.asarray(action, dtype=np.float64), -1.0, 1.0)
    v = a[0] * V_MAX if a[0] >= 0 else a[0] * -V_MIN
    return float(v), float(a[1] * W_MAX)

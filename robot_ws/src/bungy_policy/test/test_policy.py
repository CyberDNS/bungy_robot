import json
import os

import numpy as np
import pytest

from bungy_policy.interface import OBS_DIM, action_to_twist, bin_scan, make_observation

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models', 'rob-s0')


def test_observation_shape_and_range():
    angles = np.linspace(-np.pi, np.pi, 360, endpoint=False)
    bins = bin_scan(angles, np.full(360, 2.0))
    obs = make_observation(bins, (1.0, 0.5), 0.1, 0.0)
    assert obs.shape == (OBS_DIM,) and obs.dtype == np.float32
    assert np.all(np.abs(obs) <= 1.0)


def test_box_ahead_is_sector_zero():
    angles = np.linspace(-np.pi, np.pi, 360, endpoint=False)
    ranges = np.full(360, 3.0)
    ranges[np.abs(angles) < 0.05] = 0.4
    assert bin_scan(angles, ranges).argmin() in (0, 35)


def test_model_matches_json_and_runs():
    ort = pytest.importorskip('onnxruntime')
    meta = json.load(open(os.path.join(MODEL_DIR, 'policy.json')))
    assert meta['input']['shape'][1] == OBS_DIM
    sess = ort.InferenceSession(os.path.join(MODEL_DIR, 'policy.onnx'), providers=['CPUExecutionProvider'])
    out = sess.run(None, {'obs': np.zeros((1, OBS_DIM), np.float32)})[0][0]
    v, w = action_to_twist(out)
    assert -0.15 <= v <= 0.3 and -1.0 <= w <= 1.0

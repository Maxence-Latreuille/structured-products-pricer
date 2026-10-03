import numpy as np

from pricer.models import gbm_paths_from_shocks, simulate_gbm_paths

def test_paths_match_hand_calculation():
    Z = np.array([[-0.4, -1.5, 0.2, -0.5, -0.3]])
    paths = gbm_paths_from_shocks(100, 0.03, 0.2, [1, 2, 3, 4, 5], Z)
    expected = np.array([[93.24, 69.77, 73.34, 67.03, 63.76]])
    assert np.allclose(paths, expected, 1e-2)

def test_discounted_mean_equals_spot():
    times = np.array([1, 2, 3, 4, 5], dtype=float)
    paths = simulate_gbm_paths(100, 0.03, 0.2, times)
    discounted = paths * np.exp(-0.03 * times)
    means = discounted.mean(axis=0)
    std_errors = discounted.std(axis=0, ddof=1) / np.sqrt(paths.shape[0])
    assert np.all(np.abs(means - 100) < 3 * std_errors)
"""Regression checks for effective generator inputs and variance reporting."""
import numpy as np
import pytest
from src.abtest.simulate import generate_experiment
from src.abtest.cuped import cuped_variance_reduction_multi


def test_default_saved_activation_counts_remain_reproducible():
    data = generate_experiment(4230, true_lift=0.25, seed=42)
    assert data.groupby("variant")["activated"].sum().to_dict() == {
        "control": 395, "treatment": 482,
    }


def test_requested_baseline_changes_generated_outcomes():
    low = generate_experiment(20000, baseline_activation_rate=0.09, seed=13)
    high = generate_experiment(20000, baseline_activation_rate=0.27, seed=13)
    assert high["activated"].mean() - low["activated"].mean() > 0.15


@pytest.mark.parametrize("baseline", [0, 1, -0.1, float("nan")])
def test_invalid_baseline_is_rejected(baseline):
    with pytest.raises(ValueError):
        generate_experiment(100, baseline_activation_rate=baseline)


def test_equivalent_n_gain_uses_variance_ratio():
    data = generate_experiment(4230, true_lift=0.25, seed=42)
    result = cuped_variance_reduction_multi(
        data, "revenue", ["pre_exp_sessions", "pre_exp_feature_depth"]
    )
    assert result["reduction_pct"] == pytest.approx(4.34, abs=0.01)
    assert result["effective_sample_gain_pct"] == pytest.approx(4.54, abs=0.01)
    assert result["effective_sample_gain_pct"] > result["reduction_pct"]

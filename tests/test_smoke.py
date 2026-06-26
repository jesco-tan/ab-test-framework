"""Smoke tests for A/B test framework."""

import numpy as np
import pandas as pd
import pytest

from src.abtest.simulate import generate_experiment, simulate_pvalue_distribution
from src.abtest.power import required_sample_size, mde_curve
from src.abtest.frequentist import two_proportion_ztest, welch_ttest, segment_analysis
from src.abtest.bayesian import probability_treatment_better, rope_decision
from src.abtest.cuped import apply_cuped_multi, cuped_variance_reduction_multi


@pytest.fixture
def experiment_data():
    return generate_experiment(
        n_users=2000,
        baseline_activation_rate=0.18,
        true_lift=0.25,
        seed=1,
    )


def test_generate_experiment(experiment_data):
    df = experiment_data
    assert set(df["variant"]) == {"control", "treatment"}
    assert df["activated"].dtype == bool
    assert df["day1_dropoff"].dtype == bool
    assert (df["revenue"] >= 0).all()
    assert set(df["company_size"]).issubset({"solo", "small_team", "large_team"})
    assert set(df["acquisition_channel"]).issubset({"organic", "paid", "referral"})
    assert "pre_exp_sessions" in df.columns
    assert "pre_exp_feature_depth" in df.columns


def test_required_sample_size():
    n = required_sample_size(0.18, 0.20, alpha=0.05, power=0.80)
    assert 1000 < n < 10000


def test_mde_curve():
    df = mde_curve(0.18, n_per_group_range=(500, 20000), n_points=10)
    assert df["mde_relative"].is_monotonic_decreasing


def test_ztest(experiment_data):
    ctrl = experiment_data[experiment_data["variant"] == "control"]["activated"]
    trt  = experiment_data[experiment_data["variant"] == "treatment"]["activated"]
    result = two_proportion_ztest(ctrl, trt)
    assert "p_value" in result
    assert 0 <= result["p_value"] <= 1


def test_ztest_null():
    pvals = simulate_pvalue_distribution(
        500, baseline_activation_rate=0.18, true_lift=0.0, n_simulations=200, seed=99
    )
    type_i = (pvals < 0.05).mean()
    assert 0.01 < type_i < 0.15  # wide tolerance for 200 simulations


def test_bayesian(experiment_data):
    ctrl = experiment_data[experiment_data["variant"] == "control"]["activated"]
    trt  = experiment_data[experiment_data["variant"] == "treatment"]["activated"]
    result = probability_treatment_better(ctrl, trt)
    assert 0 <= result["prob_treatment_better"] <= 1


def test_cuped_multi(experiment_data):
    df_adj = apply_cuped_multi(
        experiment_data, "revenue", ["pre_exp_sessions", "pre_exp_feature_depth"]
    )
    assert "revenue_cuped" in df_adj.columns
    stats = cuped_variance_reduction_multi(
        experiment_data, "revenue", ["pre_exp_sessions", "pre_exp_feature_depth"]
    )
    assert stats["reduction_pct"] >= 0


def test_segment_analysis(experiment_data):
    seg_df = segment_analysis(experiment_data, "company_size", "activated")
    assert set(seg_df["segment"]) == {"solo", "small_team", "large_team"}
    assert "rel_lift_pct" in seg_df.columns
    assert (seg_df["p_value"] >= 0).all()
    assert (seg_df["p_value"] <= 1).all()

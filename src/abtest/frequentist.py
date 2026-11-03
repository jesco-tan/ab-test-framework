"""Frequentist A/B test methods: z-test, t-test, sequential testing, segment analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass


@dataclass
class TestResult:
    metric: str
    control_mean: float
    treatment_mean: float
    absolute_lift: float
    relative_lift_pct: float
    p_value: float
    ci_lower: float
    ci_upper: float
    significant: bool
    method: str


def two_proportion_ztest(
    control: pd.Series,
    treatment: pd.Series,
    alpha: float = 0.05,
) -> dict:
    """Two-proportion z-test for binary metrics (conversion / activation rates)."""
    n_c, n_t = len(control), len(treatment)
    p_c = control.mean()
    p_t = treatment.mean()

    p_pool = (control.sum() + treatment.sum()) / (n_c + n_t)
    se     = np.sqrt(p_pool * (1 - p_pool) * (1 / n_c + 1 / n_t))
    z      = (p_t - p_c) / se if se > 0 else 0.0
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    se_ci   = np.sqrt(p_c * (1 - p_c) / n_c + p_t * (1 - p_t) / n_t)
    z_crit  = stats.norm.ppf(1 - alpha / 2)
    delta   = p_t - p_c

    return {
        "metric":            "activation_rate",
        "control_mean":      round(p_c, 6),
        "treatment_mean":    round(p_t, 6),
        "absolute_lift":     round(delta, 6),
        "relative_lift_pct": round(delta / p_c * 100, 2) if p_c > 0 else 0.0,
        "p_value":           round(float(p_value), 6),
        "ci_lower":          round(delta - z_crit * se_ci, 6),
        "ci_upper":          round(delta + z_crit * se_ci, 6),
        "significant":       bool(p_value < alpha),
        "method":            "two_proportion_z",
        "n_control":         n_c,
        "n_treatment":       n_t,
        "z_stat":            round(float(z), 4),
    }


def welch_ttest(
    control: pd.Series,
    treatment: pd.Series,
    alpha: float = 0.05,
    metric_name: str = "revenue",
) -> dict:
    """Welch's t-test for continuous metrics (e.g. revenue per user)."""
    t_stat, p_value = stats.ttest_ind(control, treatment, equal_var=False)
    delta = treatment.mean() - control.mean()
    n_c, n_t = len(control), len(treatment)

    var_c, var_t = control.var(ddof=1), treatment.var(ddof=1)
    se = np.sqrt(var_c / n_c + var_t / n_t)
    df_welch = (var_c / n_c + var_t / n_t) ** 2 / (
        (var_c / n_c) ** 2 / (n_c - 1) + (var_t / n_t) ** 2 / (n_t - 1)
    )
    t_crit = stats.t.ppf(1 - alpha / 2, df_welch)

    return {
        "metric":            metric_name,
        "control_mean":      round(float(control.mean()), 4),
        "treatment_mean":    round(float(treatment.mean()), 4),
        "absolute_lift":     round(float(delta), 4),
        "relative_lift_pct": round(delta / control.mean() * 100, 2) if control.mean() != 0 else 0.0,
        "p_value":           round(float(p_value), 6),
        "ci_lower":          round(float(delta - t_crit * se), 4),
        "ci_upper":          round(float(delta + t_crit * se), 4),
        "significant":       bool(p_value < alpha),
        "method":            "welch_t",
        "n_control":         n_c,
        "n_treatment":       n_t,
        "t_stat":            round(float(t_stat), 4),
    }


def sequential_test(
    control: pd.Series,
    treatment: pd.Series,
    max_looks: int = 10,
    alpha: float = 0.05,
    spending_fn: str = "obrien_fleming",
) -> pd.DataFrame:
    """
    Illustrate retrospective interim looks, without validated error control.

    Splits already-collected data into `max_looks` equal batches to emulate interim
    analyses. Cumulative spending is compared directly with pointwise p-values,
    which does not calibrate joint stopping boundaries. The Pocock-labelled
    branch is linear spending, not a calibrated Pocock test. Do not use this
    function for live stopping decisions. Floor-sized batches and rounded
    p-values are retained for compatibility with the saved illustration.
    """
    n = min(len(control), len(treatment))
    # Reset index so .iloc slicing works correctly on both series
    control   = control.reset_index(drop=True)
    treatment = treatment.reset_index(drop=True)

    batch_size = n // max_looks
    records = []
    stopped = False

    for look in range(1, max_looks + 1):
        k = look * batch_size
        c = control.iloc[:k]
        t = treatment.iloc[:k]
        result = two_proportion_ztest(c, t, alpha=alpha)

        if spending_fn == "obrien_fleming":
            info_frac = look / max_looks
            alpha_boundary = 2 * (
                1 - stats.norm.cdf(stats.norm.ppf(1 - alpha / 2) / np.sqrt(info_frac))
            )
        else:  # Pocock
            alpha_boundary = alpha * look / max_looks

        p_val = result["p_value"]
        if not stopped and p_val < alpha_boundary:
            stopped = True

        records.append({
            "look":              look,
            "n_cumulative":      k * 2,
            "p_value":           p_val,
            "alpha_boundary":    round(alpha_boundary, 6),
            "significant":       stopped,
            "relative_lift_pct": result["relative_lift_pct"],
        })

        if stopped:
            break

    return pd.DataFrame(records)


def segment_analysis(
    df: pd.DataFrame,
    segment_col: str,
    metric_col: str,
    variant_col: str = "variant",
    alpha: float = 0.05,
    metric_type: str = "binary",
) -> pd.DataFrame:
    """
    Run per-segment hypothesis tests and return a forest-plot-ready DataFrame.

    Parameters
    ----------
    segment_col : column to split on (e.g. 'company_size')
    metric_col  : metric to test (e.g. 'activated')
    metric_type : 'binary' uses z-test; 'continuous' uses Welch t-test

    Returns
    -------
    DataFrame with one row per segment: rates, relative lift, 95% CI (relative),
    p-value, significance flag.
    """
    records = []
    for seg_val in sorted(df[segment_col].unique()):
        mask = df[segment_col] == seg_val
        ctrl = df[mask & (df[variant_col] == "control")][metric_col]
        trt  = df[mask & (df[variant_col] == "treatment")][metric_col]

        if metric_type == "binary":
            r = two_proportion_ztest(ctrl, trt, alpha=alpha)
        else:
            r = welch_ttest(ctrl, trt, alpha=alpha, metric_name=metric_col)

        p_c = r["control_mean"]
        # Rescaled absolute interval; omits uncertainty in the control denominator.
        rel_lo = r["ci_lower"] / p_c * 100 if p_c > 0 else 0.0
        rel_hi = r["ci_upper"] / p_c * 100 if p_c > 0 else 0.0

        records.append({
            "segment":        seg_val,
            "n_control":      r["n_control"],
            "n_treatment":    r["n_treatment"],
            "control_rate":   round(p_c, 4),
            "treatment_rate": round(r["treatment_mean"], 4),
            "rel_lift_pct":   round(r["relative_lift_pct"], 1),
            "ci_lower_pct":   round(rel_lo, 1),
            "ci_upper_pct":   round(rel_hi, 1),
            "p_value":        r["p_value"],
            "significant":    r["significant"],
        })

    return pd.DataFrame(records)

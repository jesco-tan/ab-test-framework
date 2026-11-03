"""Synthetic experiment data generator, SaaS onboarding wizard A/B test."""

from __future__ import annotations

import numpy as np
import pandas as pd

# ── Segment-level parameters ─────────────────────────────────────────────────

_SIZE_LABELS = ["solo", "small_team", "large_team"]
_SIZE_PROBS  = [0.40,   0.45,         0.15]

# Baseline week-1 activation rate per segment
_BASE_CVR = {"solo": 0.12, "small_team": 0.20, "large_team": 0.28}

# Relative lift *shape* per segment (normalised so weighted mean = true_lift)
_SEG_LIFT_SHAPE = {"solo": 0.10, "small_team": 0.28, "large_team": 0.18}

# Revenue: (paid_conversion_rate, paid_arpu) for activated users only
_REVENUE_PARAMS = {
    "solo":       (0.05, 29.0),   # 5% go paid at ~$29
    "small_team": (0.28, 42.0),   # 28% go paid, blended $29–$99 → ~$42
    "large_team": (0.40, 78.0),   # 40% go paid, mostly $99 → ~$78
}

# Guardrail: day-1 drop-off baseline; wizard adds friction in treatment
_DROPOFF_BASE = {"solo": 0.40, "small_team": 0.32, "large_team": 0.22}
_DROPOFF_WIZARD_DELTA = 0.04   # +4 pp absolute in treatment arm

# Pre-experiment covariate baselines (Poisson lambda / Normal mean)
_SESSION_LAMBDA = {"solo": 3.0, "small_team": 6.5, "large_team": 13.0}
_DEPTH_MEAN     = {"solo": 2.0, "small_team": 4.5, "large_team": 7.5}


# ── Internal helpers ──────────────────────────────────────────────────────────

def _lift_scale(true_lift: float) -> float:
    """
    Compute the scale factor that makes the population-weighted relative lift
    equal to `true_lift`.

    overall_baseline = Σ_s p_s · base_s
    treatment_CVR    = Σ_s p_s · base_s · (1 + shape_s · scale)
    true_lift        = (treatment_CVR - baseline) / baseline
    → scale = baseline · true_lift / Σ_s(p_s · base_s · shape_s)
    """
    weighted_base  = sum(_SIZE_PROBS[i] * _BASE_CVR[s]
                         for i, s in enumerate(_SIZE_LABELS))
    weighted_shape = sum(_SIZE_PROBS[i] * _BASE_CVR[s] * _SEG_LIFT_SHAPE[s]
                         for i, s in enumerate(_SIZE_LABELS))
    return weighted_base * true_lift / weighted_shape


# ── Public API ────────────────────────────────────────────────────────────────

def generate_experiment(
    n_users: int,
    baseline_activation_rate: float = 0.18,
    true_lift: float = 0.0,
    traffic_split: float = 0.5,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate a user-level SaaS onboarding A/B test dataset.

    Parameters
    ----------
    n_users : total enrolled users
    baseline_activation_rate : weighted segment baseline before quality/clipping
    true_lift : desired overall relative lift in treatment (0.25 = +25% relative)
    traffic_split : fraction allocated to treatment
    seed : random seed for reproducibility

    Returns
    -------
    DataFrame with columns:
        user_id, variant, company_size, acquisition_channel,
        activated, revenue, day1_dropoff,
        pre_exp_sessions, pre_exp_feature_depth
    """
    if not 0 < baseline_activation_rate < 1:
        raise ValueError("baseline_activation_rate must be between 0 and 1")
    if not 0 < traffic_split < 1 or n_users < 2:
        raise ValueError("Use at least two records and a traffic_split between 0 and 1")
    if not np.isfinite(true_lift) or true_lift < -1:
        raise ValueError("true_lift must be finite and at least -1")
    # 0.18 is the original profile's weighted baseline. Preserve the original
    # default execution while making other requested baselines effective.
    baseline_scale = baseline_activation_rate / 0.18
    rng = np.random.default_rng(seed)
    n_treatment = int(n_users * traffic_split)
    n_control   = n_users - n_treatment

    channel_labels = ["organic", "paid", "referral"]
    channel_probs  = [0.50,      0.35,   0.15]

    scale = _lift_scale(true_lift) if true_lift != 0.0 else 0.0

    def make_group(n: int, variant: str) -> pd.DataFrame:
        is_treatment = variant == "treatment"

        # Segment assignment
        sizes    = rng.choice(_SIZE_LABELS, size=n, p=_SIZE_PROBS)
        channels = rng.choice(channel_labels, size=n, p=channel_probs)

        base_cvr  = np.array([_BASE_CVR[s] * baseline_scale for s in sizes])
        seg_shape = np.array([_SEG_LIFT_SHAPE[s]  for s in sizes])

        # Latent user quality: drives within-segment covariate→outcome correlation
        quality = rng.standard_normal(n)

        # Pre-experiment covariates (recorded before experiment launch)
        session_lam = np.array([_SESSION_LAMBDA[s] for s in sizes])
        pre_exp_sessions = np.maximum(
            0, rng.poisson(session_lam + np.maximum(0, quality * 2.5))
        ).astype(int)

        depth_mu = np.array([_DEPTH_MEAN[s] for s in sizes])
        pre_exp_feature_depth = np.clip(
            depth_mu + quality * 1.8 + rng.normal(0, 0.4, n), 1.0, 10.0
        ).round(1)

        # Activation (primary metric)
        # Quality adds up to ±4 pp individual variation around segment baseline
        cvr = np.clip(base_cvr + 0.04 * quality, 0.01, 0.99)
        if is_treatment:
            cvr = np.clip(cvr + base_cvr * seg_shape * scale, 0.01, 0.99)
        activated = rng.binomial(1, cvr).astype(bool)

        # Revenue (secondary metric), zero-inflated; only activated users can pay
        paid_rate = np.array([_REVENUE_PARAMS[s][0] for s in sizes])
        paid_arpu = np.array([_REVENUE_PARAMS[s][1] for s in sizes])
        goes_paid = rng.random(n) < paid_rate
        raw_revenue = rng.lognormal(
            mean=np.log(paid_arpu) - 0.5 * 0.3 ** 2,
            sigma=0.3,
            size=n,
        )
        revenue = np.where(activated & goes_paid, raw_revenue, 0.0).round(2)

        # Day-1 drop-off (guardrail), wizard adds friction
        dropoff_base = np.array([_DROPOFF_BASE[s] for s in sizes])
        dropoff_p = np.clip(
            dropoff_base + (_DROPOFF_WIZARD_DELTA if is_treatment else 0.0),
            0.0, 0.99,
        )
        day1_dropoff = rng.binomial(1, dropoff_p).astype(bool)

        return pd.DataFrame({
            "user_id":               [f"{variant}_{i}" for i in range(n)],
            "variant":               variant,
            "company_size":          sizes,
            "acquisition_channel":   channels,
            "activated":             activated,
            "revenue":               revenue,
            "day1_dropoff":          day1_dropoff,
            "pre_exp_sessions":      pre_exp_sessions,
            "pre_exp_feature_depth": pre_exp_feature_depth,
        })

    control   = make_group(n_control,   "control")
    treatment = make_group(n_treatment, "treatment")
    return pd.concat([control, treatment], ignore_index=True)


def simulate_pvalue_distribution(
    n_users: int,
    baseline_activation_rate: float,
    true_lift: float,
    n_simulations: int = 500,
    seed: int = 0,
) -> np.ndarray:
    """Run many experiments and return z-test p-values (used for calibration checks)."""
    from src.abtest.frequentist import two_proportion_ztest

    pvals = []
    for i in range(n_simulations):
        df = generate_experiment(
            n_users, baseline_activation_rate, true_lift=true_lift, seed=seed + i
        )
        ctrl = df[df["variant"] == "control"]["activated"]
        trt  = df[df["variant"] == "treatment"]["activated"]
        pvals.append(two_proportion_ztest(ctrl, trt)["p_value"])
    return np.array(pvals)

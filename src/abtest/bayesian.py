"""Bayesian A/B testing using Beta-Binomial conjugate model."""

from __future__ import annotations

import numpy as np
import pandas as pd


def beta_posterior(
    n_conversions: int,
    n_trials: int,
    prior_alpha: float = 1.0,
    prior_beta: float = 1.0,
) -> tuple[float, float]:
    """Return (alpha, beta) of the posterior Beta distribution."""
    return prior_alpha + n_conversions, prior_beta + (n_trials - n_conversions)


def probability_treatment_better(
    control: pd.Series,
    treatment: pd.Series,
    prior_alpha: float = 1.0,
    prior_beta: float = 1.0,
    n_samples: int = 100_000,
    seed: int = 42,
) -> dict:
    """
    Monte Carlo estimate of P(treatment > control) and expected lift.

    Returns dict with probability, expected_lift, credible_interval.
    """
    rng = np.random.default_rng(seed)

    a_c, b_c = beta_posterior(int(control.sum()), len(control), prior_alpha, prior_beta)
    a_t, b_t = beta_posterior(int(treatment.sum()), len(treatment), prior_alpha, prior_beta)

    samples_c = rng.beta(a_c, b_c, size=n_samples)
    samples_t = rng.beta(a_t, b_t, size=n_samples)

    lift_samples = (samples_t - samples_c) / samples_c
    prob_better = float((samples_t > samples_c).mean())
    expected_lift = float(lift_samples.mean())
    ci_lo, ci_hi = float(np.percentile(lift_samples, 2.5)), float(np.percentile(lift_samples, 97.5))

    return {
        "prob_treatment_better": round(prob_better, 4),
        "expected_relative_lift_pct": round(expected_lift * 100, 2),
        "lift_95pct_credible_interval": (round(ci_lo * 100, 2), round(ci_hi * 100, 2)),
        "control_posterior": (a_c, b_c),
        "treatment_posterior": (a_t, b_t),
        "n_samples": n_samples,
    }


def rope_decision(
    control: pd.Series,
    treatment: pd.Series,
    rope_width: float = 0.001,
    prior_alpha: float = 1.0,
    prior_beta: float = 1.0,
    n_samples: int = 100_000,
    seed: int = 42,
) -> dict:
    """
    Region of Practical Equivalence (ROPE) decision.

    Returns: 'treatment_wins', 'control_wins', or 'equivalent'.
    """
    rng = np.random.default_rng(seed)
    a_c, b_c = beta_posterior(int(control.sum()), len(control), prior_alpha, prior_beta)
    a_t, b_t = beta_posterior(int(treatment.sum()), len(treatment), prior_alpha, prior_beta)

    samples_c = rng.beta(a_c, b_c, size=n_samples)
    samples_t = rng.beta(a_t, b_t, size=n_samples)
    delta = samples_t - samples_c

    p_in_rope = float((np.abs(delta) < rope_width).mean())
    p_treatment_wins = float((delta > rope_width).mean())
    p_control_wins = float((delta < -rope_width).mean())

    if p_in_rope > 0.95:
        decision = "equivalent"
    elif p_treatment_wins > 0.95:
        decision = "treatment_wins"
    elif p_control_wins > 0.95:
        decision = "control_wins"
    else:
        decision = "inconclusive"

    return {
        "decision": decision,
        "p_treatment_wins": round(p_treatment_wins, 4),
        "p_control_wins": round(p_control_wins, 4),
        "p_equivalent_rope": round(p_in_rope, 4),
        "rope_width": rope_width,
    }


def posterior_samples(
    n_conversions: int,
    n_trials: int,
    prior_alpha: float = 1.0,
    prior_beta: float = 1.0,
    n_samples: int = 10_000,
    seed: int = 42,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    a, b = beta_posterior(n_conversions, n_trials, prior_alpha, prior_beta)
    return rng.beta(a, b, size=n_samples)

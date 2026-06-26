"""Power analysis and MDE calculations."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def required_sample_size(
    baseline_cvr: float,
    mde: float,
    alpha: float = 0.05,
    power: float = 0.80,
    two_sided: bool = True,
) -> int:
    """
    Return the per-group sample size needed to detect a relative lift of `mde`.

    Uses the exact two-proportion formula (not the approximation).
    """
    p1 = baseline_cvr
    p2 = baseline_cvr * (1 + mde)
    z_alpha = stats.norm.ppf(1 - alpha / (2 if two_sided else 1))
    z_beta = stats.norm.ppf(power)

    p_bar = (p1 + p2) / 2
    se_null = np.sqrt(2 * p_bar * (1 - p_bar))
    se_alt = np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))

    n = ((z_alpha * se_null + z_beta * se_alt) / (p2 - p1)) ** 2
    return int(np.ceil(n))


def mde_curve(
    baseline_cvr: float,
    n_per_group_range: tuple[int, int] = (100, 50_000),
    alpha: float = 0.05,
    power: float = 0.80,
    n_points: int = 60,
) -> pd.DataFrame:
    """Return a DataFrame of (n_per_group, detectable_relative_mde) pairs."""
    ns = np.logspace(
        np.log10(n_per_group_range[0]),
        np.log10(n_per_group_range[1]),
        n_points,
    ).astype(int)

    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    records = []
    for n in ns:
        # Invert the formula: given n, what absolute effect is detectable?
        p = baseline_cvr
        se = np.sqrt(2 * p * (1 - p) / n)
        delta = (z_alpha + z_beta) * se
        mde_rel = delta / p
        records.append({"n_per_group": int(n), "mde_relative": round(mde_rel, 4)})

    return pd.DataFrame(records)


def power_by_sample_size(
    baseline_cvr: float,
    true_lift: float,
    n_range: tuple[int, int] = (100, 50_000),
    alpha: float = 0.05,
    n_points: int = 60,
) -> pd.DataFrame:
    """Return a DataFrame of (n_per_group, power) pairs for a fixed true lift."""
    ns = np.logspace(np.log10(n_range[0]), np.log10(n_range[1]), n_points).astype(int)
    p1 = baseline_cvr
    p2 = baseline_cvr * (1 + true_lift)
    z_alpha = stats.norm.ppf(1 - alpha / 2)

    records = []
    for n in ns:
        se = np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n)
        z = (p2 - p1) / se - z_alpha
        pwr = stats.norm.cdf(z)
        records.append({"n_per_group": int(n), "power": round(float(pwr), 4)})

    return pd.DataFrame(records)

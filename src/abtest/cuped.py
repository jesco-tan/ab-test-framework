"""CUPED (Controlled-experiment Using Pre-Experiment Data) variance reduction."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def apply_cuped(
    df: pd.DataFrame,
    metric_col: str,
    covariate_col: str,
    variant_col: str = "variant",
) -> pd.DataFrame:
    """
    Apply single-covariate CUPED adjustment.

    Y_cuped = Y - θ(X - mean(X))    where  θ = Cov(Y, X) / Var(X)

    Equivalent to regressing out a single pre-experiment covariate.
    """
    df = df.copy()
    cov_matrix = df[[metric_col, covariate_col]].cov()
    theta  = cov_matrix.iloc[0, 1] / df[covariate_col].var()
    x_bar  = df[covariate_col].mean()
    df[f"{metric_col}_cuped"] = df[metric_col] - theta * (df[covariate_col] - x_bar)
    return df


def cuped_variance_reduction(
    df: pd.DataFrame,
    metric_col: str,
    covariate_col: str,
) -> dict:
    """Quantify variance reduction from single-covariate CUPED."""
    df_adj = apply_cuped(df, metric_col, covariate_col)
    var_original = df[metric_col].var()
    var_adjusted = df_adj[f"{metric_col}_cuped"].var()
    reduction_pct = (1 - var_adjusted / var_original) * 100
    r = np.corrcoef(df[metric_col], df[covariate_col])[0, 1]

    theta = df[[metric_col, covariate_col]].cov().iloc[0, 1] / df[covariate_col].var()

    return {
        "variance_original":        round(var_original, 4),
        "variance_cuped":           round(var_adjusted, 4),
        "reduction_pct":            round(reduction_pct, 2),
        "effective_sample_gain_pct": round(reduction_pct, 2),
        "pearson_r":                round(float(r), 4),
        "theta":                    round(float(theta), 6),
    }


def apply_cuped_multi(
    df: pd.DataFrame,
    metric_col: str,
    covariate_cols: list[str],
    variant_col: str = "variant",
) -> pd.DataFrame:
    """
    Multi-covariate CUPED via OLS projection.

    Y_cuped = Y - X_c @ θ
    where X_c = column-centred covariate matrix and θ = OLS(Y ~ X_c).

    This is identical to partialling out multiple pre-experiment covariates
    and preserves the mean of Y (no intercept shift).
    """
    from numpy.linalg import lstsq

    df = df.copy()
    Y   = df[metric_col].values.astype(float)
    X   = df[covariate_cols].values.astype(float)
    X_c = X - X.mean(axis=0)   # centre each covariate

    theta, _, _, _ = lstsq(X_c, Y, rcond=None)
    df[f"{metric_col}_cuped"] = Y - X_c @ theta
    return df


def cuped_variance_reduction_multi(
    df: pd.DataFrame,
    metric_col: str,
    covariate_cols: list[str],
) -> dict:
    """
    Quantify variance reduction from multi-covariate CUPED.

    Returns reduction percentage, per-covariate Pearson r with the metric,
    and the equivalent sample size gain (reduction_pct ≈ R² of the OLS regression).
    """
    df_adj    = apply_cuped_multi(df, metric_col, covariate_cols)
    var_orig  = df[metric_col].var()
    var_cuped = df_adj[f"{metric_col}_cuped"].var()
    reduction_pct = (1 - var_cuped / var_orig) * 100

    corr = df[[metric_col] + covariate_cols].corr()
    r_per_covariate = {
        col: round(float(corr.loc[metric_col, col]), 4)
        for col in covariate_cols
    }

    return {
        "variance_original":        round(var_orig, 4),
        "variance_cuped":           round(var_cuped, 4),
        "reduction_pct":            round(reduction_pct, 2),
        "effective_sample_gain_pct": round(reduction_pct, 2),
        "pearson_r_per_covariate":  r_per_covariate,
        "r_squared_approx":         round(reduction_pct / 100, 4),
    }

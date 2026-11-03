"""Plotting helpers for A/B test framework."""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import seaborn as sns
from pathlib import Path

sns.set_theme(style="whitegrid", palette="muted")

_BLUE   = "#4472C4"
_ORANGE = "#ED7D31"
_GREEN  = "#70AD47"
_RED    = "#C0504D"
_GRAY   = "#9E9E9E"


# ── Existing plots (unchanged) ────────────────────────────────────────────────

def plot_power_curves(
    power_df: pd.DataFrame,
    mde_df: pd.DataFrame,
    save_path: Path | None = None,
) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    axes[0].plot(power_df["n_per_group"], power_df["power"] * 100, color=_BLUE, linewidth=2)
    axes[0].axhline(80, color="red", linestyle="--", linewidth=1, label="80% power target")
    axes[0].set_xlabel("Users per Group")
    axes[0].set_ylabel("Power (%)")
    axes[0].set_title("Statistical Power vs Sample Size")
    axes[0].legend()
    axes[0].set_xscale("log")

    axes[1].plot(mde_df["n_per_group"], mde_df["mde_relative"] * 100, color=_ORANGE, linewidth=2)
    axes[1].set_xlabel("Users per Group")
    axes[1].set_ylabel("Minimum Detectable Effect (%)")
    axes[1].set_title("MDE vs Sample Size")
    axes[1].set_xscale("log")

    plt.tight_layout()
    fig.text(0.5, -0.02, "Synthetic scenario; no measured business outcome.", ha="center", fontsize=9)
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_posterior(
    control_samples: np.ndarray,
    treatment_samples: np.ndarray,
    prob_better: float,
    save_path: Path | None = None,
) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(13, 4))

    axes[0].hist(control_samples,   bins=80, alpha=0.6, color=_BLUE,   label="Control",   density=True)
    axes[0].hist(treatment_samples, bins=80, alpha=0.6, color=_ORANGE, label="Treatment", density=True)
    axes[0].set_title("Posterior Distributions, Activation Rate")
    axes[0].set_xlabel("Activation Rate")
    axes[0].set_ylabel("Density")
    axes[0].legend()

    lift_samples = (treatment_samples - control_samples) / control_samples * 100
    axes[1].hist(lift_samples, bins=80, color=_GREEN, edgecolor="white", density=True)
    axes[1].axvline(0, color="red", linewidth=1.5, linestyle="--")
    axes[1].set_title(f"Posterior Lift Distribution\nP(treatment > control) = {prob_better:.1%}")
    axes[1].set_xlabel("Relative Lift (%)")
    axes[1].set_ylabel("Density")

    plt.tight_layout()
    fig.text(0.5, -0.02, "Synthetic scenario; no measured business outcome.", ha="center", fontsize=9)
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_pvalue_distribution(
    pvals_h0: np.ndarray,
    pvals_h1: np.ndarray,
    alpha: float = 0.05,
    save_path: Path | None = None,
) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(13, 4))

    axes[0].hist(pvals_h0, bins=40, color=_BLUE, edgecolor="white", density=True)
    axes[0].axvline(alpha, color="red", linestyle="--", linewidth=1.5, label=f"α = {alpha}")
    axes[0].set_title("p-value Distribution Under H₀ (no true effect)\n→ should be Uniform[0,1]")
    axes[0].set_xlabel("p-value")
    axes[0].legend()
    type_i = (pvals_h0 < alpha).mean()
    axes[0].text(0.6, 0.85, f"Type I error: {type_i:.1%}", transform=axes[0].transAxes,
                 bbox=dict(boxstyle="round", facecolor="wheat"), fontsize=10)

    axes[1].hist(pvals_h1, bins=40, color=_ORANGE, edgecolor="white", density=True)
    axes[1].axvline(alpha, color="red", linestyle="--", linewidth=1.5, label=f"α = {alpha}")
    axes[1].set_title("p-value Distribution Under H₁ (true effect = MDE)\n→ should be skewed left")
    axes[1].set_xlabel("p-value")
    axes[1].legend()
    power = (pvals_h1 < alpha).mean()
    axes[1].text(0.6, 0.85, f"Empirical power: {power:.1%}", transform=axes[1].transAxes,
                 bbox=dict(boxstyle="round", facecolor="wheat"), fontsize=10)

    plt.tight_layout()
    fig.text(0.5, -0.02, "Synthetic scenario; no measured business outcome.", ha="center", fontsize=9)
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_sequential_path(
    sequential_df: pd.DataFrame,
    save_path: Path | None = None,
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(sequential_df["n_cumulative"], sequential_df["p_value"],
            marker="o", color=_BLUE, label="p-value")
    ax.plot(sequential_df["n_cumulative"], sequential_df["alpha_boundary"],
            marker="s", linestyle="--", color="red", label="Illustrative threshold (not error-controlled)")
    ax.set_xlabel("Cumulative generated records")
    ax.set_ylabel("p-value")
    ax.set_title("Retrospective prefix tests, not a stopping rule")
    ax.legend()
    plt.tight_layout()
    fig.text(0.5, -0.02, "Synthetic scenario; no measured business outcome.", ha="center", fontsize=9)
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


# ── New plots ─────────────────────────────────────────────────────────────────

def plot_segment_forest(
    segment_df: pd.DataFrame,
    title: str = "Heterogeneous Treatment Effects by Segment",
    overall_lift: float | None = None,
    overall_ci: tuple[float, float] | None = None,
    save_path: Path | None = None,
) -> plt.Figure:
    """
    Forest plot of relative lift (%) with 95% CI per segment.

    segment_df must have columns: segment, rel_lift_pct, ci_lower_pct,
    ci_upper_pct, significant.
    """
    df = segment_df.copy().reset_index(drop=True)
    n  = len(df)

    fig, ax = plt.subplots(figsize=(9, max(3, n * 0.9 + 1.5)))

    colors = [_BLUE if sig else _GRAY for sig in df["significant"]]
    y_pos  = np.arange(n)

    for i, row in df.iterrows():
        color = colors[i]
        ax.plot(row["rel_lift_pct"], i, "o", color=color, ms=8, zorder=3)
        ax.plot(
            [row["ci_lower_pct"], row["ci_upper_pct"]], [i, i],
            "-", color=color, linewidth=2, zorder=2,
        )
        # Annotation: lift + p-value
        ax.text(
            max(df["ci_upper_pct"]) + 2, i,
            f"{row['rel_lift_pct']:+.1f}%  (p={row['p_value']:.3f})",
            va="center", fontsize=9, color=color,
        )

    # Overall lift reference line
    ax.axvline(0, color="black", linewidth=1, linestyle="--", zorder=1)
    if overall_lift is not None:
        ax.axvline(overall_lift, color="green", linewidth=1.5,
                   linestyle=":", label=f"Overall lift {overall_lift:+.1f}%")
        if overall_ci:
            ax.axvspan(overall_ci[0], overall_ci[1], alpha=0.08, color="green")
        ax.legend(fontsize=9)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(df["segment"], fontsize=10)
    ax.set_xlabel("Relative Lift (%)")
    ax.set_title(title)

    # Legend patches
    patches = [
        mpatches.Patch(color=_BLUE, label="Significant (p < 0.05)"),
        mpatches.Patch(color=_GRAY, label="Not significant"),
    ]
    ax.legend(handles=patches, loc="lower right", fontsize=9)

    plt.tight_layout()
    fig.text(0.5, -0.02, "Synthetic scenario; no measured business outcome.", ha="center", fontsize=9)
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_revenue_distribution(
    control_rev: pd.Series,
    treatment_rev: pd.Series,
    save_path: Path | None = None,
) -> plt.Figure:
    """
    Two-panel revenue plot for zero-inflated data.

    Left:  bar chart, % of users with $0 vs positive revenue in each arm.
    Right: histogram of positive-revenue users only (excludes zeros).
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 4))

    # Panel 1: zero vs positive share
    zero_c = (control_rev   == 0).mean() * 100
    zero_t = (treatment_rev == 0).mean() * 100
    pos_c  = 100 - zero_c
    pos_t  = 100 - zero_t

    x = np.array([0, 1])
    width = 0.35
    axes[0].bar(x - width / 2, [zero_c, pos_c], width, label="Control",   color=_BLUE,   alpha=0.8)
    axes[0].bar(x + width / 2, [zero_t, pos_t], width, label="Treatment", color=_ORANGE, alpha=0.8)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(["$0 (no revenue)", "Positive revenue"])
    axes[0].set_ylabel("% of Users")
    axes[0].set_title("Revenue Split, Zero vs Positive")
    axes[0].legend()

    # Panel 2: distribution of positive revenue
    pos_ctrl_vals = control_rev[control_rev > 0]
    pos_trt_vals  = treatment_rev[treatment_rev > 0]
    axes[1].hist(pos_ctrl_vals, bins=40, alpha=0.6, color=_BLUE,   label="Control",   density=True)
    axes[1].hist(pos_trt_vals,  bins=40, alpha=0.6, color=_ORANGE, label="Treatment", density=True)
    axes[1].set_xlabel("Revenue ($)")
    axes[1].set_ylabel("Density")
    axes[1].set_title("Revenue Distribution, Paying Users Only")
    axes[1].legend()

    plt.tight_layout()
    fig.text(0.5, -0.02, "Synthetic scenario; no measured business outcome.", ha="center", fontsize=9)
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_metric_scorecard(
    results: list[dict],
    save_path: Path | None = None,
) -> plt.Figure:
    """
    Visual metric scorecard table.

    Each dict in `results` must have:
        label, role ('primary'/'secondary'/'guardrail'),
        control_mean, treatment_mean, rel_lift_pct, p_value, significant,
        direction ('higher_better' or 'lower_better')
    """
    n = len(results)
    fig, ax = plt.subplots(figsize=(12, 0.7 * n + 1.2))
    ax.axis("off")

    col_labels = ["Metric", "Role", "Control", "Treatment", "Lift", "p-value", "Decision"]
    col_widths = [0.20, 0.10, 0.10, 0.10, 0.10, 0.10, 0.15]

    # Header row
    x = 0.0
    for label, w in zip(col_labels, col_widths):
        ax.text(x + w / 2, 1.0, label, ha="center", va="center",
                fontweight="bold", fontsize=10,
                transform=ax.transAxes)
        x += w

    row_height = 0.8 / n
    for row_idx, r in enumerate(results):
        y = 0.85 - row_idx * row_height

        sig = r["significant"]
        higher_better = r["direction"] == "higher_better"

        # Colour logic
        if sig and higher_better:
            bg = "#C6EFCE"   # green
            decision = "✓ Ship"
        elif sig and not higher_better:
            bg = "#FFC7CE"   # red, guardrail breached
            decision = "✗ Concern"
        elif not sig and not higher_better:
            bg = "#FFEB9C"   # yellow, guardrail not breached
            decision = "~ OK"
        else:
            bg = "#FFEB9C"   # yellow, not significant
            decision = "~ Neutral"

        row_data = [
            r["label"],
            r["role"].capitalize(),
            f"{r['control_mean']:.3f}",
            f"{r['treatment_mean']:.3f}",
            f"{r['rel_lift_pct']:+.1f}%",
            f"{r['p_value']:.4f}",
            decision,
        ]

        x = 0.0
        for val, w in zip(row_data, col_widths):
            ax.add_patch(plt.Rectangle(
                (x, y - row_height * 0.45), w, row_height * 0.9,
                color=bg, transform=ax.transAxes, zorder=1,
            ))
            ax.text(x + w / 2, y, val, ha="center", va="center",
                    fontsize=9, transform=ax.transAxes, zorder=2)
            x += w

    ax.set_title("Metric Scorecard", fontsize=12, fontweight="bold", pad=10)
    plt.tight_layout()
    fig.text(0.5, -0.02, "Synthetic scenario; no measured business outcome.", ha="center", fontsize=9)
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig

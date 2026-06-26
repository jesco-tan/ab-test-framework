# A/B Testing Framework

A portfolio project demonstrating a rigorous experimentation framework across the full experiment lifecycle, from pre-experiment power planning to a structured ship/no-ship decision. All analysis runs on a realistic synthetic SaaS dataset; no external data required.

## The Experiment

**Question**: Does a guided 5-step setup wizard improve week-1 activation in a B2B project-management SaaS product?

| | Control | Treatment |
|---|---|---|
| Experience | Blank free-explore dashboard | Guided wizard: create project → invite teammate → set due date → enable notifications → complete first task |
| Users | 2,115 | 2,115 |
| Activation rate | 18.7% | 22.8% |

**Result**: +22% relative lift in activation (p = 0.001), with a significant guardrail breach in day-1 drop-off, producing a nuanced segment-specific recommendation rather than a simple ship/no-ship.

## What this demonstrates

| Technique | Implementation |
|---|---|
| Power analysis | Exact two-proportion formula; MDE curve; sensitivity table at 5 lift levels |
| Frequentist testing | Two-proportion z-test (activation); Welch t-test (revenue); sequential O'Brien-Fleming |
| Segment analysis | Per-segment z-tests with forest plot, heterogeneous effects across `company_size` and `acquisition_channel` |
| Bayesian inference | Beta-Binomial conjugate with informative prior Beta(18,82); P(treatment better); ROPE decision |
| CUPED | Multi-covariate OLS variance reduction using `pre_exp_sessions` + `pre_exp_feature_depth` |
| Calibration | Monte Carlo p-value distributions under H₀ and H₁; empirical Type I error and power |
| Guardrail monitoring | Three-metric scorecard (primary / secondary / guardrail) with visual traffic-light table |

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
jupyter notebook notebooks/ab_test_walkthrough.ipynb  # Run All
pytest tests -q
```

## Notebook structure

| Section | What it covers |
|---|---|
| 1. Pre-experiment planning | Required N = 1,923/group; power sensitivity table |
| 2. Experiment data | 4,230 synthetic users with segments, covariates, guardrail |
| 3. EDA | Activation by segment; revenue distribution; covariate balance |
| 4. Primary metric | Z-test: +4.1 pp absolute, p = 0.001 |
| 5. Segment analysis | Forest plots by company_size and acquisition_channel |
| 6. Secondary metric | Revenue/user: +14.8% but p = 0.33 (underpowered for noisy metric) |
| 7. Guardrail | Day-1 drop-off: +5.3 pp, p = 0.0003, breached |
| 8. Sequential monitoring | Would have stopped at look 4 (60% of planned N) |
| 9. Bayesian analysis | P(better) = 99.9%; ROPE → treatment_wins |
| 10. CUPED | 4.3% variance reduction on revenue; CI tightened |
| 11. Calibration | Type I error 4.0%; empirical power 78.5% |
| 12. Decision framework | Segment-specific recommendation with scorecard |

## Key outputs

| File | Description |
|---|---|
| `outputs/power_curves.png` | Power vs N and MDE vs N |
| `outputs/segment_forest_size.png` | Forest plot, lift by company_size |
| `outputs/segment_forest_channel.png` | Forest plot, lift by acquisition channel |
| `outputs/posterior_lift.png` | Bayesian posterior distributions and lift histogram |
| `outputs/revenue_distribution.png` | Zero-inflated revenue split (zero vs positive) |
| `outputs/sequential_test.png` | Sequential p-value path vs O'Brien-Fleming boundary |
| `outputs/pvalue_sim_distribution.png` | Calibration under H₀ and H₁ |
| `outputs/metric_scorecard.png` | Traffic-light scorecard for all three metrics |
| `outputs/run_summary.json` | All numeric results |

## Project structure

```
config/experiment.yaml        Baseline rates, MDE, alpha, power, priors, segment list
src/abtest/
  simulate.py                 Data generator, segments, HTE, zero-inflated revenue, guardrail
  power.py                    Required N, MDE curve, power-by-N curve
  frequentist.py              Z-test, Welch t-test, sequential O'Brien-Fleming, segment_analysis()
  bayesian.py                 Beta-Binomial posteriors, P(better), ROPE decision
  cuped.py                    Single- and multi-covariate CUPED via OLS projection
  visualise.py                Power curves, posterior, forest plot, scorecard, revenue distribution
notebooks/
  ab_test_walkthrough.ipynb   Full 12-section pipeline
outputs/                      Generated charts + run_summary.json (committed)
tests/test_smoke.py           8 correctness checks
```

## Tech stack

`scipy` · `numpy` · `pandas` · `matplotlib` · `seaborn` · `pyyaml`

No PyMC, Stan, or heavy probabilistic dependencies, the Beta-Binomial conjugate model is analytically tractable.

## See also

[`REPORT.md`](REPORT.md), full methodology, all experimental results with commentary, and the final decision recommendation.

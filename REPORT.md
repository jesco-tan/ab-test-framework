# A fixed-horizon experimentation framework

Executed 3 November 2026. All example outcomes and validation experiments are synthetic. No commercial impact or live release is claimed.

## Reference design

Fixed horizon, two independent arms, two-sided alpha 0.05. Planning at baseline 18% and relative MDE 20% requires 1,923 observations per arm. The test uses pooled null variance; its Wald confidence interval uses unpooled alternative variance. Planning and plotted power now use matching null and alternative variances; MDE curves invert the sizing calculation. These normal approximations differ by design and are not exactly equivalent in finite samples.

Early stopping is disabled: `sequential_test` raises an explicit error. There is no supported O'Brien-Fleming or Pocock procedure and no early-stopping recommendation. Expected total sample size is always 3,846 in the calibrated reference design.

## Calibration

Seed 20261103. 10,000 complete experiments per binary effect give about 0.0043 Monte Carlo half-width around a 5% error rate. Exact binomial 95% Monte Carlo intervals accompany rejection rates. Simulations use independent Bernoulli outcomes, rather than the richer demonstration generator.

| Absolute effect | Rejection rate | Monte Carlo interval | Difference CI coverage |
| --- | --- | --- | --- |
| 0.000 | 0.0511 | [0.0469, 0.0556] | 0.9489 |
| 0.018 | 0.3015 | [0.2925, 0.3106] | 0.9530 |
| 0.036 | 0.7931 | [0.7850, 0.8010] | 0.9476 |
| 0.054 | 0.9840 | [0.9813, 0.9864] | 0.9497 |

The fixed-horizon null rejection rate and planned-MDE power pass the predefined simulation tolerances recorded in `inference_validation.json`. This validates these settings, not every baseline, small sample or stopping scheme.

## Covariate-adjusted inference

The supported estimator is the treatment coefficient in a regression on treatment and centered pre-experiment covariates, using HC3 robust variance and asymptotic normal intervals. Testing fitted adjusted residuals with a naive t-test is not the validated procedure. Existing CUPED variance summaries remain descriptive helpers.

Eight scenarios combine null/effect 0.2, covariate mean shift 0/0.75 and normal/centered lognormal errors, with 300 observations per arm and 2,000 simulations each. Deliberate covariate shifts are a regression stress test, not randomized-balance evidence. Bias, interval coverage, rejection rate and standard errors are recorded separately. The model is additive and correctly specified; this does not validate arbitrary confounding, nonlinear effects or extreme tails.

| Covariate shift | Skewed errors | True effect | Bias | CI coverage | Adjusted mean SE |
| --- | --- | --- | --- | --- | --- |
| 0.0 | False | 0.0 | 0.0008 | 0.9470 | 0.0819 |
| 0.0 | False | 0.2 | 0.0014 | 0.9485 | 0.0819 |
| 0.0 | True | 0.0 | 0.0008 | 0.9510 | 0.1067 |
| 0.0 | True | 0.2 | -0.0019 | 0.9425 | 0.1058 |
| 0.75 | False | 0.0 | 0.0028 | 0.9490 | 0.0875 |
| 0.75 | False | 0.2 | -0.0007 | 0.9600 | 0.0875 |
| 0.75 | True | 0.0 | 0.0042 | 0.9475 | 0.1128 |
| 0.75 | True | 0.2 | -0.0000 | 0.9605 | 0.1131 |

Each scenario passes the predefined coverage and bias tolerances. Monte Carlo intervals and raw estimator standard errors are in the JSON. Single-seed calibration is finite evidence, not proof of universal coverage.

## Subgroups and release criteria

Per-segment p-values receive Holm correction within each segment family. Relative-lift intervals use a delta method with variance from both arm means; they remain approximate and unstable near a zero control mean. A zero denominator produces a missing interval rather than a spurious zero-width interval. Intervals are pointwise, not simultaneous after multiplicity adjustment.

Differences between segments are tested with a joint treatment-by-segment HC3 Wald test on the additive scale. The two demonstrated segment-family interaction tests receive Holm correction together. A significant within-segment effect does not establish an interaction.

The illustrative scorecard requires a positive lower 95% primary-effect bound and a guardrail upper bound below a predeclared absolute harm margin of two percentage points. A nonsignificant harm test does not establish guardrail acceptability. The current generated sample fails the release criterion. The margin is a demonstration setting, not a real stakeholder-approved business tolerance.

## Reproduce

Python 3.14, isolated `.venv`, install pinned `requirements.txt`. Run `.venv/Scripts/python.exe -m pytest tests -q -p no:cacheprovider`, then `.venv/Scripts/python.exe scripts/validate_inference.py` and `python scripts/generate_html_report.py`. The manifest records package versions, source hashes, seed, output hashes and tolerance. The notebook calls this same runner. Older plots in outputs are historical and are not current calibration evidence.

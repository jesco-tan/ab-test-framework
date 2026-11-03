# Validation

I checked the fixed-horizon reference tests, covariate-adjusted estimator, subgroup procedures and release criteria. All 19 Python tests and the predefined simulation calibration passed.

I simulated 10,000 complete binary experiments per effect and 2,000 covariate-adjustment experiments per scenario. The saved results report rejection rates, bias, interval coverage and Monte Carlo uncertainty against tolerances specified before simulation. Early stopping is disabled.

## Scope

Calibration supports the documented fixed-horizon settings and additive regression scenarios. It does not validate arbitrary outcome distributions, confounded observational comparisons or a sequential stopping procedure. The harm margin is an illustrative business assumption. See [REPORT.md](REPORT.md), `outputs/inference_validation.json` and `outputs/inference_manifest.json` for the designs and reproduction.

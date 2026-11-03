# A synthetic experimentation framework: planning, inference and decision limits

Implemented a synthetic SaaS experiment workflow with approximate power planning, fixed-horizon tests, Bayesian inference, covariate adjustment and a three-metric scorecard. Saved results illustrate planted effects; sequential error control and segment rollout claims remain unvalidated.

I built a Python framework to connect experiment planning, inference and decision-making. Its published run uses 4,230 synthetic user records for a hypothetical SaaS onboarding wizard. No real users were enrolled, no feature was shipped and no business improvement was measured.

The framework covers normal-approximation power planning, binary and continuous outcome tests, Beta-Binomial inference, exploratory segments, multi-covariate adjustment and a primary/secondary/guardrail scorecard. Auditing its outputs also exposed statistical and reporting limits that need to remain visible.

## Read the results

[REPORT.md](REPORT.md) gives the supported results, assumptions and limitations. [report.html](report.html) contains the same interpretation with embedded figures. The [walkthrough notebook](notebooks/ab_test_walkthrough.ipynb) retains numerical evidence and corrected narrative. The corrected synthetic notebook was executed in an isolated environment; outputs/execution-environment.json records package versions. Old wording and reports are available through Git history.

No real users, customers, bank-disclosure measurements or policy effects are represented by this saved run.

## Reproduce or inspect

Render the current report without dependencies or analytical execution:

```powershell
python scripts/generate_html_report.py
```

Run the synthetic notebook in an isolated environment (this overwrites analytical outputs):

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
# Install notebook tooling inside the same virtual environment if needed.
.venv/Scripts/python.exe -m pip install jupyter
.venv/Scripts/python.exe -m jupyter notebook notebooks/ab_test_walkthrough.ipynb
.venv/Scripts/python.exe -m pytest tests -q
```

Install analytical dependencies only in a project virtual environment.

## Evidence and implementation limits

Python experimentation framework demonstrated on synthetic SaaS records, with approximate power planning, fixed-horizon tests, Bayesian inference and covariate adjustment.

See [REPORT.md](REPORT.md) for method definitions, synthetic results and remaining analytical limitations.

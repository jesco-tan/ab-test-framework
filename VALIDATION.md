# Verification, 3 November 2026

15 Python tests passed, including default activation counts, effective baseline inputs and variance-ratio reporting. The corrected synthetic notebook was executed in a workspace virtual environment and its figures regenerated. It reproduced 395 and 482 activations across 2,115 records per arm. CUPED equivalent-N gain is 4.54%. Guardrail absolute_change_pp is correctly multiplied by 100 in schema version 2. Runtime versions are in outputs/execution-environment.json.

## Interpretation limits

The current results are synthetic demonstrations. Passing software checks does not validate real-world predictive performance, causality or business benefit.

The interim-look function remains an explicitly illustrative, unvalidated stopping method. Subgroup comparisons are exploratory, and adjusted Welch inference after pooled CUPED remains provisional.

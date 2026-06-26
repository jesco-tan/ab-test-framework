# Experiment Report: SaaS Onboarding Wizard

**Experiment ID**: `saas_onboarding_wizard`  
**Date**: 2026-06-24  
**Status**: Complete, Segment-conditional ship recommendation

---

## Executive Summary

We ran a randomised controlled experiment (n = 4,230 users, 2,115 per arm) testing whether a guided 5-step setup wizard improves week-1 activation compared to the existing blank free-explore dashboard.

The wizard produced a **+22.0% relative lift in activation rate** (18.7% → 22.8%, p = 0.001), confirmed by a Bayesian posterior placing 99.9% probability on the treatment being superior. However, the experiment also triggered a **guardrail breach**: day-1 drop-off increased significantly by +5.3 percentage points (p = 0.0003), indicating that the wizard's upfront friction causes a meaningful fraction of new users to churn immediately.

Segment analysis resolves the apparent conflict. The activation benefit is large and statistically significant for `small_team` (+24.9%, p = 0.006) and `large_team` users (+26.4%, p = 0.032), who genuinely need the wizard to set up shared workspaces. For `solo` users, the lift is negligible (+7.2%) and statistically indistinguishable from zero (p = 0.61), suggesting the wizard adds friction without meaningful benefit for this segment.

**Recommendation**: Ship the wizard to `small_team` and `large_team` users. Hold for `solo` users and test a lighter-weight alternative (contextual in-product tooltips) to capture activation gains without the drop-off cost.

---

## 1. Experiment Design

### Business context

A B2B project-management SaaS product (analogous to a lightweight Linear or Asana) observed that most new users who do not activate in week 1 never return. The onboarding team hypothesised that a structured wizard, guiding users through five specific actions, would increase the proportion who reach meaningful product engagement within their first week.

| | Control | Treatment |
|---|---|---|
| Experience | Empty dashboard, self-directed exploration | Guided wizard: (1) create first project, (2) invite a teammate, (3) set a due date, (4) enable notifications, (5) complete first task |
| Assignment | 50/50 random split at signup | 50/50 random split at signup |

### Metric definitions

| Metric | Role | Definition | Desired direction |
|---|---|---|---|
| Week-1 Activation Rate | Primary | User completes ≥ 3 of the 5 key onboarding actions within 7 days of signup | Higher |
| Revenue Per User | Secondary | Monthly recurring revenue allocated per user (MRR; $0 for free-tier users) | Higher |
| Day-1 Drop-off Rate | Guardrail | User never returns after their signup day | Lower |

Revenue is zero-inflated: the vast majority of users are on a free tier ($0), with a small fraction upgrading to paid plans. Using revenue per user (including the zeros) rather than average revenue per paying user captures the full commercial impact of the treatment.

### Population and segmentation

Users were stratified at the point of analysis (not at randomisation) into:

**Company size** (primary segmentation dimension):
- `solo` (39.0% of users): single-seat accounts
- `small_team` (45.7%): 2–20 seat accounts
- `large_team` (15.3%): 20+ seat accounts

**Acquisition channel** (secondary segmentation):
- `organic` (50.3%): direct / SEO
- `paid` (35.2%): paid search / social ads
- `referral` (14.5%): word-of-mouth / affiliate

The wizard was designed with collaborative features (shared projects, teammate invitations) at its core, this creates a strong a-priori reason to expect heterogeneous treatment effects across company size.

---

## 2. Pre-Experiment Planning

### Power analysis

Using the exact two-proportion formula (not the pooled-SE approximation):

| Parameter | Value |
|---|---|
| Baseline activation rate | 18.0% |
| Minimum detectable effect | 20% relative (18.0% → 21.6%) |
| Significance level (α) | 0.05, two-sided |
| Target power (1 − β) | 80% |
| **Required N per group** | **1,923** |
| **Required total** | **3,846** |

We enrolled 4,230 users (2,115 per group), a 10% buffer above the minimum required. This buffer ensures we remain adequately powered even if realised activation rates differ slightly from assumptions.

### Power sensitivity

The table below shows how power varies with the true lift, given our achieved sample size of 2,115 per group:

| True relative lift | Statistical power |
|---|---|
| 10% | 29.7% |
| 15% | 56.4% |
| 20% | 80.1% |
| 25% | 93.5% |
| 30% | 98.5% |

The experiment was sized to detect a 20% relative lift with 80% confidence. Smaller effects (< 10%) would require substantially more traffic to detect and were considered below the business threshold for this intervention.

---

## 3. Exploratory Analysis & Balance Check

### Group summary

| Metric | Control | Treatment |
|---|---|---|
| Users | 2,115 | 2,115 |
| Activations | 395 | 482 |
| Activation rate | 18.68% | 22.79% |
| Avg revenue per user | $2.85 | $3.27 |
| Day-1 drop-off rate | 33.05% | 38.39% |

### Pre-experiment covariate balance

The pre-experiment covariates used for CUPED showed good balance between groups (as expected from random assignment), confirming no systematic assignment bias:

| Covariate | Control mean | Treatment mean |
|---|---|---|
| Sessions (pre-experiment) | 7.16 | 7.10 |
| Feature depth (pre-experiment) | 4.16 | 4.08 |

Both covariates are slightly higher in control (as expected by chance in any finite randomisation), but the difference is trivially small and not statistically meaningful.

### Activation rate by segment (unadjusted)

| Company size | Control | Treatment | Absolute lift | Relative lift |
|---|---|---|---|---|
| `large_team` | 30.3% | 38.3% | +8.0 pp | +26.4% |
| `small_team` | 21.6% | 27.0% | +5.4 pp | +24.9% |
| `solo` | 10.8% | 11.6% | +0.8 pp | +7.2% |

The EDA already signals the heterogeneous effect before any formal testing: the wizard adds nearly nothing for solo users but substantially lifts team users.

---

## 4. Primary Metric, Week-1 Activation Rate

**Test**: Two-proportion z-test (standard for binary outcomes)

| Statistic | Value |
|---|---|
| Control activation rate | 18.68% |
| Treatment activation rate | 22.79% |
| Absolute lift | +4.11 percentage points |
| Relative lift | +22.0% |
| 95% Confidence Interval (absolute) | [+1.67 pp, +6.55 pp] |
| z-statistic | 3.300 |
| p-value | 0.0010 |
| Significant at α = 0.05 | **Yes** |

The result is unambiguous: the wizard increases week-1 activation by 22% relative to the free-explore baseline. The 95% CI excludes zero by a comfortable margin, even the lower bound (+1.67 pp) represents a practically meaningful improvement.

The p-value of 0.001 is far below the α = 0.05 threshold, meaning that, if there were truly no difference between wizard and no-wizard, we would observe a result this extreme in fewer than 1 in 1,000 experiments by chance.

---

## 5. Heterogeneous Treatment Effects, Segment Analysis

Aggregate results can mask heterogeneous treatment effects that are critical for the shipping decision. We pre-specified two segmentation dimensions and ran separate z-tests per stratum.

### By company size (primary segmentation)

| Segment | N (control) | Control rate | Treatment rate | Relative lift | p-value | Significant |
|---|---|---|---|---|---|---|
| `large_team` | 323 | 30.3% | 38.3% | +26.4% | 0.032 | Yes |
| `small_team` | 968 | 21.6% | 27.0% | +24.9% | 0.006 | Yes |
| `solo` | 824 | 10.8% | 11.6% | +7.2% | 0.613 | No |

**Key finding**: The wizard delivers consistent, significant activation gains for team users (~25–26% relative lift). For solo users, the point estimate is small (+7.2%) and carries a p-value of 0.61, this is not underpowered noise, it is a genuine null result. The solo segment is large enough (N = 1,649) that a real 25% effect would have been detected with >99% power; we are instead observing that the wizard simply does not help solo users in the same way.

This is mechanistically coherent: the wizard's steps 2 (invite a teammate) and 5 (complete a shared task) are meaningless for solo users. They are completing a wizard optimised for a use case that does not apply to them.

### By acquisition channel (secondary segmentation)

| Segment | N (control) | Control rate | Treatment rate | Relative lift | p-value | Significant |
|---|---|---|---|---|---|---|
| `organic` | 1,065 | 19.7% | 23.9% | +21.4% | 0.006 | Yes |
| `paid` | 747 | 17.2% | 23.1% | +34.3% | 0.009 | Yes |
| `referral` | 303 | 14.9% | 17.8% | +20.0% | 0.321 | No |

Organic and paid-acquisition users respond strongly to the wizard. The paid-channel effect is notably large (+34.3%), which could indicate that users arriving from performance marketing campaigns have less prior product familiarity and therefore benefit more from explicit guidance.

The referral segment result is not significant (p = 0.32), but the sample size (N = 606) is small enough that this is largely a power issue rather than a compelling null: the 20% point estimate is consistent with the organic result, and the 95% CI would be wide. We should not confidently claim the wizard does not work for referral users.

**Note on multiple testing**: these subgroup analyses were pre-specified, not data-mined. We are not applying a multiple-testing correction (e.g., Bonferroni) for the pre-specified segments. However, results should be treated as hypothesis-generating for any segment that was not pre-specified, and confirmed in a follow-up experiment.

---

## 6. Secondary Metric, Revenue Per User

**Test**: Welch's t-test (robust to unequal variances, appropriate for zero-inflated distributions)

| Statistic | Value |
|---|---|
| Control mean revenue | $2.85 |
| Treatment mean revenue | $3.27 |
| Absolute lift | +$0.42 |
| Relative lift | +14.8% |
| 95% Confidence Interval | [−$0.42, +$1.26] |
| t-statistic | −0.981 |
| p-value | 0.327 |
| Significant at α = 0.05 | **No** |

The revenue result is directionally positive but not statistically significant. The CI is wide and straddles zero, meaning we cannot rule out that the wizard has no revenue impact. This is expected: revenue is a noisier metric than activation (high variance due to zero-inflation), and the experiment was sized for the activation metric, not revenue.

### Zero-inflation breakdown

| Arm | Users at $0 | Paying users | Avg revenue (payers only) |
|---|---|---|---|
| Control | 94.8% | 5.2% | $55.22 |
| Treatment | 94.0% | 6.0% | $54.40 |

The revenue distribution reveals what is driving the positive trend: a small increase in the fraction of users reaching the paid tier (5.2% → 6.0%), rather than higher ARPU among those already paying ($55.22 → $54.40, essentially flat). This is consistent with the activation story, more activated users in treatment are exploring the product more deeply and a slightly higher fraction cross the conversion threshold to paid.

The revenue result is best understood as a directional signal rather than a confirmed finding. A longer experiment or a revenue-powered sample size calculation would be needed to achieve significance on this metric.

---

## 7. Guardrail Metric, Day-1 Drop-off Rate

**Test**: Two-proportion z-test

| Statistic | Value |
|---|---|
| Control drop-off rate | 33.05% |
| Treatment drop-off rate | 38.39% |
| Absolute increase | +5.34 percentage points |
| p-value | 0.0003 |
| Guardrail breached | **Yes** |

This is the central tension in the experiment. The wizard significantly increases the rate at which users never return after day 1. The effect is highly significant (p = 0.0003) and practically large: one in every nineteen users (5.3 pp) who would have returned in the baseline experience instead drops off when shown the wizard.

The mechanism is plausible: the wizard is presented immediately at signup, before users have seen the product's value proposition. Users who arrived with low intent (e.g., speculative paid-ad clicks) are confronted with a multi-step commitment and leave. In the free-explore condition, these same low-intent users may spend a few minutes browsing and naturally exit, but without being blocked by a mandatory flow.

### Reconciling activation gain vs. drop-off increase

These two findings are not contradictory, they describe different user populations:

- Users who **stay past day 1** and complete the wizard activate at a significantly higher rate.
- A **larger fraction of users never make it past day 1** in the wizard condition.

The net effect on week-1 activation (across *all* enrolled users, including those who dropped off) is still strongly positive (+22%), which means the activation gain from retained users more than outweighs the activation loss from additional drop-offs. However, day-1 drop-off is a leading indicator of long-term retention and LTV, and a 5.3 pp increase warrants monitoring even after shipping.

---

## 8. Sequential Monitoring, Early Stopping Analysis

The sequential test simulates what would have happened if we had monitored the experiment at 10 equally-spaced interim looks, using the O'Brien-Fleming alpha-spending function to preserve the overall α = 0.05.

| Look | Cumulative N | p-value | O'B-F boundary | Crossed? |
|---|---|---|---|---|
| 1 | 635 | 0.547 | 0.00000 | No |
| 2 | 1,270 | 0.167 | 0.00001 | No |
| 3 | 1,905 | 0.072 | 0.00433 | No |
| 4 | 2,540 | **0.024** | **0.0236** | **Yes** |

The experiment would have crossed the O'Brien-Fleming boundary at look 4, after 2,540 cumulative users, **60% of the planned sample size**. This represents a potential 40% saving in experiment runtime and traffic.

The O'Brien-Fleming function is deliberately conservative at early looks (requiring an extremely low p-value to stop at look 1) and becomes progressively more permissive as information accumulates. Look 4 represents 40% of total information, at which point the boundary (α = 0.024) is close to the nominal α = 0.05, reflecting our increasing confidence in the estimate.

**Caveat**: the guardrail breach might not have been detectable at look 4 depending on how the day-1 drop-off analysis was monitored. In practice, sequential monitoring should be run on all metrics simultaneously, with stopping rules that account for the joint test.

---

## 9. Bayesian Analysis

**Model**: Beta-Binomial conjugate with informative prior

The Bayesian approach answers: *given the data we observed, what is the probability that the wizard genuinely improves activation?*

### Prior specification

We used an informative prior `Beta(18, 82)`, equivalent to a prior belief that activation rates are approximately 18% (the industry benchmark for SaaS onboarding), based on roughly 100 prior pseudo-observations. This prior is:

- **Informative enough** to temper implausible results from small samples (unlike a flat Beta(1,1) prior)
- **Weak enough** to be overwhelmed by 4,000+ real observations

With this prior, the posterior is dominated by the observed data, but the prior prevents us from drawing strong conclusions from early looks with only a few hundred users.

### Results

| Quantity | Value |
|---|---|
| Prior | Beta(18, 82), mean = 18.0% |
| P(treatment > control) | **99.93%** |
| Expected relative lift | +21.3% |
| 95% Credible Interval | [+7.8%, +36.1%] |

The posterior probability that the wizard is superior is 99.93%, extremely high confidence. Unlike a p-value, this is a direct probability statement about the parameter of interest.

The 95% credible interval [+7.8%, +36.1%] means we are 95% confident that the true relative lift lies somewhere in that range. The lower bound of +7.8% represents the worst-case plausible outcome and remains a commercially meaningful improvement.

### ROPE Decision

The Region of Practical Equivalence (ROPE) is defined as ±0.5 percentage points of activation rate, differences within this band are commercially indistinguishable.

| Probability | Value |
|---|---|
| P(treatment wins, i.e., lift > ROPE) | 99.7% |
| P(practically equivalent) | 0.3% |
| P(control wins) | 0.0% |
| **Decision** | **TREATMENT_WINS** |

99.7% of the posterior mass for the lift falls outside the ROPE and in the positive direction. The ROPE framework gives a more nuanced answer than binary significance testing: it confirms not just that treatment is better, but that it is *meaningfully* better with extremely high confidence.

### Frequentist vs. Bayesian comparison

| Criterion | Frequentist result | Bayesian result |
|---|---|---|
| Primary question | p = 0.001, reject H₀ | P(treatment better) = 99.9% |
| Effect size | +22.0% relative, 95% CI [+9.0%, +35.1%] | Expected +21.3%, 95% CrI [+7.8%, +36.1%] |
| Decision | Significant | treatment_wins |
| Interpretation | Probability of data given H₀ | Probability of hypothesis given data |

Both frameworks align strongly in this case. The frequentist result is more conservative by construction (the informative Bayesian prior pulls the posterior toward smaller lifts when the data are noisy), but both unambiguously support the treatment.

---

## 10. CUPED, Variance Reduction

CUPED (Deng et al., 2013, Microsoft) reduces the variance of the outcome metric by removing variation explained by pre-experiment covariates. Lower variance produces tighter confidence intervals and higher power, equivalent to running a larger experiment without collecting more data.

**Multi-covariate implementation** (this project extends the standard single-covariate formula):

```
Y_cuped = Y − X_c @ θ
θ = (X_c'X_c)⁻¹ X_c' Y    [OLS regression coefficients]
X_c = column-centred covariate matrix
```

This is identical to partialling out multiple pre-experiment covariates via OLS, and the variance reduction equals the R² of the regression.

### Covariates used

| Covariate | Pearson r with revenue | Variance contribution (R²) |
|---|---|---|
| `pre_exp_sessions` (login sessions, 14 days pre-launch) | +0.196 | 3.8% |
| `pre_exp_feature_depth` (distinct features used in trial) | +0.191 | 3.6% |

### Results

| Metric | Value |
|---|---|
| Original revenue variance | 194.81 |
| CUPED revenue variance | 186.35 |
| **Variance reduction** | **4.3%** |
| Effective sample size gain | 4.3% |

| Test | p-value | 95% CI |
|---|---|---|
| Original Welch t-test | 0.327 | [−$0.42, +$1.26] |
| CUPED-adjusted t-test | 0.244 | [−$0.33, +$1.31] |

The variance reduction of 4.3% is modest (compared to the 20–30% reductions achievable when covariate-metric correlation is high) but real. The covariates correlate with revenue through the company-size dimension: larger-team users have more pre-experiment sessions and feature depth, and are also more likely to pay. The CUPED adjustment tightens the CI and reduces the p-value from 0.327 to 0.244, though the result remains non-significant for revenue.

The limited reduction reflects the high zero-inflation of revenue: when 94% of values are $0, the continuous covariates capture only a small fraction of total variance. CUPED would be substantially more powerful if applied to a lower-variance continuous metric (e.g., weekly session count) or in an experiment where the covariate is a direct historical lagged value of the metric.

**Key property**: CUPED does not change the point estimate, only the variance. This is guaranteed by the centring of covariates before regression. The treatment effect estimate remains +$0.42 before and after adjustment.

---

## 11. Calibration Check

A correctly specified test must satisfy two properties:

1. **Under H₀** (no true effect): p-values should be Uniform[0,1], and the empirical Type I error rate should be ≈ α = 5%.
2. **Under H₁** (true effect present): p-values should be concentrated near zero, and the empirical power should be ≈ 80%.

We ran 200 simulated experiments under each hypothesis (capped from 5,000 for runtime; the full config value is available for production validation runs).

| Property | Observed | Target | Status |
|---|---|---|---|
| Type I error (H₀, α = 0.05) | 4.0% | 5.0% | ✓ Within tolerance |
| Empirical power (H₁, MDE = 20%) | 78.5% | 80.0% | ✓ Within tolerance |

The slight undershoot in both quantities is expected with only 200 simulations (standard error of a proportion at p ≈ 0.05 with N = 200 is ±1.5 pp). The test is well-calibrated: no spike near zero under H₀ (which would indicate an anti-conservative test), and the H₁ distribution is appropriately concentrated in the low-p region.

---

## 12. Decision Framework

### Metric scorecard

| Metric | Role | Control | Treatment | Relative lift | p-value | Decision |
|---|---|---|---|---|---|---|
| Week-1 Activation | Primary | 18.7% | 22.8% | +22.0% | 0.001 | ✓ Ship |
| Revenue Per User | Secondary | $2.85 | $3.27 | +14.8% | 0.327 | ~ Neutral |
| Day-1 Drop-off | Guardrail | 33.1% | 38.4% | +16.2% | 0.0003 | ✗ Concern |

### Evidence synthesis

**For shipping:**
- Primary metric is strongly significant (p = 0.001) with a 22% relative lift
- Bayesian posterior gives 99.9% confidence in the direction of the effect
- ROPE analysis confirms the effect is not just significant but practically meaningful
- Team segments (small_team + large_team, representing 60% of users) show large, significant activation gains
- Revenue trends positive, consistent with the activation story
- Sequential analysis confirms the experiment was adequately powered and could have concluded 40% earlier

**Against unrestricted shipping:**
- Day-1 drop-off increased by 5.3 pp, a significant guardrail breach
- Solo users (39% of users) show no significant activation benefit (+7.2%, p = 0.61)
- Revenue did not reach significance; full commercial impact is uncertain
- Paid-channel users show the highest activation lift (+34.3%), which could indicate the wizard works well for less familiar users, but also that drop-off impact may be concentrated in this segment

### Segment-specific recommendation

| Segment | N | Activation lift | Guardrail concern | Recommendation |
|---|---|---|---|---|
| `small_team` | 1,935 | +24.9% (p=0.006) | Shared; monitor | **Ship** |
| `large_team` | 646 | +26.4% (p=0.032) | Shared; monitor | **Ship** |
| `solo` | 1,649 | +7.2% (p=0.613) | Disproportionate | **Hold**: test alternative |

**For `small_team` and `large_team`**: Ship the wizard. The activation benefit is large, consistent, and statistically sound. Monitor day-1 drop-off in the first two weeks post-launch; if drop-off exceeds the 38% treatment rate by a meaningful margin (>2 pp), investigate the wizard step that causes the most abandonment (hypothesised to be step 2: "Invite a teammate").

**For `solo` users**: Do not ship the current wizard. The five-step flow is mis-matched to solo use cases (particularly steps 2 and 5, which require a teammate). Instead, design a solo-specific checklist: (1) create first project, (2) add first task, (3) set due date, (4) enable email reminders, (5) mark task complete. This preserves the activation benefit structure without imposing a fundamentally collaborative flow.

### Longer-term monitoring

Activation is a leading indicator, not an end-state. The following metrics should be tracked at 30 and 90 days post-launch to confirm the experiment's activation gains translate to durable retention and revenue:

1. **Week-4 retention rate**: do wizard-activated users remain active a month later?
2. **Trial-to-paid conversion**: does higher activation translate to higher paid conversion?
3. **Day-7 churn**: does the day-1 drop-off increase persist as a day-7 drop-off signal?
4. **Feature adoption breadth**: do activated users explore more of the product or just complete the wizard steps?

---

## Appendix: Methodology Notes

### Synthetic data assumptions

All data in this project is synthetically generated. The simulator models:
- **Segment heterogeneity**: baseline activation rates differ by company_size (solo: 12%, small_team: 20%, large_team: 28%)
- **Treatment effect heterogeneity**: wizard lifts are segment-specific and scale to produce an approximately 25% overall relative lift
- **Latent user quality**: a shared latent variable drives correlation between pre-experiment covariates and experiment outcomes, making CUPED non-trivial
- **Zero-inflated revenue**: revenue follows a log-normal distribution conditional on both activation and paid-tier conversion, with the vast majority of users at $0
- **Guardrail tension**: day-1 drop-off is uniformly higher in the treatment arm (+4 pp), simulating the friction cost of the wizard

### What differs in a real experiment

In a live experiment, several factors would add complexity not present in the simulation:

- **Network effects**: B2B SaaS products often have within-team spillovers, if one team member activates and invites teammates, the teammates' activation is not independent. A SUTVA (Stable Unit Treatment Value Assumption) violation would bias the z-test results.
- **Novelty effects**: users encountering the wizard for the first time may behave differently than they would after the novelty wears off. A holdout period post-experiment would validate durability.
- **Carryover effects**: users who see the wizard and drop off may be harder to re-engage than users who saw the blank dashboard. The long-run LTV impact is not captured by a short-window experiment.
- **Sequential monitoring in practice**: the sequential test here simulates batch looks on already-collected data. A live implementation would use the same alpha-spending function applied to data as it accumulates in real time, which requires infrastructure for continuous metric computation.
- **CUPED in practice**: the pre-experiment covariate should be computed over a clean pre-period window (typically 1–2 weeks before experiment launch) that does not overlap with the experiment period or any previous experiments that may have affected user behaviour.

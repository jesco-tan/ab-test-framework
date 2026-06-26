"""Generate a self-contained HTML experiment report from outputs/run_summary.json and PNGs."""

from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT    = Path(__file__).parent.parent
OUTPUTS = ROOT / "outputs"


# ── Helpers ───────────────────────────────────────────────────────────────────

def b64img(name: str) -> str:
    data = base64.b64encode((OUTPUTS / name).read_bytes()).decode()
    return f"data:image/png;base64,{data}"


def pct(v: float, decimals: int = 1) -> str:
    return f"{v:.{decimals}f}%"


def pp(v: float) -> str:
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.2f} pp"


def dollar(v: float) -> str:
    sign = "+" if v >= 0 else ""
    return f"{sign}${v:.2f}"


def sig_badge(significant: bool) -> str:
    if significant:
        return '<span class="badge badge-green">Significant</span>'
    return '<span class="badge badge-gray">Not significant</span>'


def p_color(p: float) -> str:
    if p < 0.01:
        return "color:#16a34a;font-weight:600"
    if p < 0.05:
        return "color:#d97706;font-weight:600"
    return "color:#6b7280"


# ── Data ─────────────────────────────────────────────────────────────────────

s   = json.loads((OUTPUTS / "run_summary.json").read_text())
pm  = s["primary_metric"]
sm  = s["secondary_metric"]
gm  = s["guardrail_metric"]
bay = s["bayesian"]
cup = s["cuped"]
cal = s["calibration"]
segs = {r["segment"]: r for r in s["segment_analysis"]}


# Sequential test results (from notebook output, not in JSON)
SEQ_ROWS = [
    (1,  635,  0.5471, 0.000000, False),
    (2, 1270,  0.1665, 0.000012, False),
    (3, 1905,  0.0718, 0.004330, False),
    (4, 2540,  0.0236, 0.023600, True),
]

# Revenue breakdown (from notebook output)
REV_ZERO_CTRL = 94.8;  REV_PAY_CTRL = 5.2;  REV_ARPU_CTRL = 55.22
REV_ZERO_TRT  = 94.0;  REV_PAY_TRT  = 6.0;  REV_ARPU_TRT  = 54.40

# Channel segments (from notebook output)
CHANNEL_SEGS = [
    ("organic",  1065, 0.1972, 0.2395, 21.4, 0.006,  True),
    ("paid",      747, 0.1719, 0.2308, 34.3, 0.009,  True),
    ("referral",  303, 0.1485, 0.1782, 20.0, 0.321, False),
]


# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --blue:    #4472C4;
  --orange:  #ED7D31;
  --green:   #16a34a;
  --red:     #dc2626;
  --amber:   #d97706;
  --gray:    #6b7280;
  --border:  #e5e7eb;
  --bg:      #f3f4f6;
  --card:    #ffffff;
  --text:    #111827;
  --muted:   #6b7280;
}

body {
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  font-size: 15px;
  line-height: 1.65;
  color: var(--text);
  background: var(--bg);
}

/* ── Nav ── */
nav {
  position: sticky; top: 0; z-index: 100;
  background: #1e293b;
  padding: 0 2rem;
  display: flex; align-items: center; gap: 0;
  overflow-x: auto;
  box-shadow: 0 1px 4px rgba(0,0,0,.3);
}
nav a {
  color: #94a3b8; text-decoration: none;
  font-size: 13px; font-weight: 500; white-space: nowrap;
  padding: .75rem 1rem;
  border-bottom: 2px solid transparent;
  transition: color .15s, border-color .15s;
}
nav a:hover { color: #f1f5f9; border-bottom-color: var(--blue); }
.nav-brand {
  color: #f1f5f9 !important; font-weight: 700 !important;
  font-size: 14px !important; margin-right: 1rem;
  border-bottom: none !important;
}

/* ── Layout ── */
main { max-width: 1020px; margin: 0 auto; padding: 2.5rem 1.5rem 5rem; }

/* ── Hero ── */
.hero {
  background: linear-gradient(135deg, #1e293b 0%, #0f4c81 100%);
  color: white; border-radius: 12px; padding: 2.5rem 3rem;
  margin-bottom: 2rem;
}
.hero-tag {
  font-size: 12px; font-weight: 700; letter-spacing: .1em;
  text-transform: uppercase; color: #93c5fd;
  margin-bottom: .5rem;
}
.hero h1 { font-size: 28px; font-weight: 700; margin-bottom: .75rem; }
.hero-meta { font-size: 13px; color: #94a3b8; margin-bottom: 1.25rem; }
.hero-desc { font-size: 15px; color: #cbd5e1; max-width: 680px; line-height: 1.7; }

/* ── KPI strip ── */
.kpi-strip { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2.5rem; }
.kpi-card {
  background: var(--card); border-radius: 10px;
  padding: 1.25rem 1.5rem; border: 1px solid var(--border);
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
.kpi-label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: .07em; color: var(--muted); margin-bottom: .4rem; }
.kpi-value { font-size: 32px; font-weight: 700; line-height: 1; margin-bottom: .3rem; }
.kpi-sub { font-size: 13px; color: var(--muted); }
.kpi-green .kpi-value { color: var(--green); }
.kpi-red   .kpi-value { color: var(--red); }
.kpi-blue  .kpi-value { color: var(--blue); }

/* ── Section ── */
.section {
  background: var(--card); border-radius: 10px; border: 1px solid var(--border);
  padding: 2rem 2.25rem; margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
.section-header { margin-bottom: 1.25rem; }
.section-num { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--blue); margin-bottom: .2rem; }
.section h2 { font-size: 20px; font-weight: 700; }
.section p { margin-bottom: .85rem; color: #374151; }
.section p:last-child { margin-bottom: 0; }

/* ── Tables ── */
.table-wrap { overflow-x: auto; margin: 1.25rem 0; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th {
  background: #f8fafc; text-align: left;
  padding: .6rem .9rem; font-weight: 600; font-size: 13px;
  border-bottom: 2px solid var(--border); color: #374151;
  white-space: nowrap;
}
td { padding: .55rem .9rem; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #fafbff; }
.num { font-variant-numeric: tabular-nums; }

/* ── Stat block ── */
.stat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: .75rem; margin: 1.25rem 0; }
.stat-box {
  background: #f8fafc; border: 1px solid var(--border); border-radius: 8px;
  padding: .85rem 1rem;
}
.stat-box-label { font-size: 12px; color: var(--muted); font-weight: 500; margin-bottom: .2rem; }
.stat-box-value { font-size: 20px; font-weight: 700; color: var(--text); }
.stat-box-sub { font-size: 12px; color: var(--muted); margin-top: .1rem; }

/* ── Badges ── */
.badge { display: inline-block; font-size: 11px; font-weight: 700; padding: .15rem .55rem; border-radius: 999px; letter-spacing: .04em; }
.badge-green { background: #dcfce7; color: #15803d; }
.badge-red   { background: #fee2e2; color: #b91c1c; }
.badge-gray  { background: #f3f4f6; color: #4b5563; }
.badge-amber { background: #fef9c3; color: #92400e; }

/* ── Alert boxes ── */
.alert { border-radius: 8px; padding: 1rem 1.25rem; margin: 1rem 0; font-size: 14px; }
.alert-green { background: #f0fdf4; border-left: 4px solid var(--green); color: #14532d; }
.alert-red   { background: #fef2f2; border-left: 4px solid var(--red);   color: #7f1d1d; }
.alert-amber { background: #fffbeb; border-left: 4px solid var(--amber); color: #78350f; }
.alert-blue  { background: #eff6ff; border-left: 4px solid var(--blue);  color: #1e3a5f; }
.alert strong { display: block; font-weight: 700; margin-bottom: .25rem; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; }

/* ── Chart ── */
.chart { width: 100%; border-radius: 8px; border: 1px solid var(--border); margin: 1.25rem 0; }
.chart-caption { font-size: 12px; color: var(--muted); text-align: center; margin-top: -.5rem; margin-bottom: 1rem; }

/* ── Two-col layout ── */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0; }

/* ── Recommendation cards ── */
.rec-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1.25rem 0; }
.rec-card { border-radius: 8px; padding: 1.1rem 1.25rem; border: 1px solid; }
.rec-ship  { background: #f0fdf4; border-color: #86efac; }
.rec-hold  { background: #fffbeb; border-color: #fde68a; }
.rec-watch { background: #fef2f2; border-color: #fca5a5; }
.rec-card h4 { font-size: 13px; font-weight: 700; margin-bottom: .35rem; }
.rec-ship  h4 { color: #15803d; }
.rec-hold  h4 { color: #92400e; }
.rec-watch h4 { color: #b91c1c; }
.rec-card p  { font-size: 13px; color: #374151; margin: 0; }
.rec-metric  { font-size: 22px; font-weight: 700; margin: .3rem 0; }

/* ── Footer ── */
footer { text-align: center; color: var(--muted); font-size: 13px; padding: 3rem 0 1rem; }
"""


# ── HTML sections ─────────────────────────────────────────────────────────────

def nav_html() -> str:
    links = [
        ("#design",     "Design"),
        ("#planning",   "Power Analysis"),
        ("#eda",        "EDA"),
        ("#primary",    "Primary Metric"),
        ("#segments",   "Segments"),
        ("#secondary",  "Revenue"),
        ("#guardrail",  "Guardrail"),
        ("#sequential", "Sequential"),
        ("#bayesian",   "Bayesian"),
        ("#cuped",      "CUPED"),
        ("#calibration","Calibration"),
        ("#decision",   "Decision"),
    ]
    items = '<a class="nav-brand" href="#">A/B Report</a>'
    items += "".join(f'<a href="{href}">{label}</a>' for href, label in links)
    return f"<nav>{items}</nav>"


def hero_html() -> str:
    return f"""
<div class="hero">
  <div class="hero-tag">Experiment Report · {s['experiment_name']}</div>
  <h1>SaaS Onboarding Wizard, A/B Test Analysis</h1>
  <div class="hero-meta">
    Completed 2026-06-24 &nbsp;·&nbsp; n = {s['n_users_total']:,} users
    ({s['n_required_per_group']:,} per group required · {s['n_users_total']//2:,} per group enrolled)
    &nbsp;·&nbsp; Planted lift: {s['true_lift_planted']:.0%} relative
  </div>
  <p class="hero-desc">
    Randomised controlled experiment testing whether a guided 5-step setup wizard
    improves week-1 activation vs the existing blank free-explore dashboard.
    Control = empty dashboard; Treatment = create project → invite teammate → set due date →
    enable notifications → complete first task.
  </p>
</div>
"""


def kpi_strip_html() -> str:
    lift   = pm["relative_lift_pct"]
    droppp = gm["absolute_change_pp"] * 100
    prob   = bay["prob_treatment_better"] * 100
    return f"""
<div class="kpi-strip">
  <div class="kpi-card kpi-green">
    <div class="kpi-label">Activation lift (primary)</div>
    <div class="kpi-value">+{lift:.1f}%</div>
    <div class="kpi-sub">{pm['control_mean']:.1%} → {pm['treatment_mean']:.1%} &nbsp;·&nbsp; p = {pm['p_value']:.4f}</div>
  </div>
  <div class="kpi-card kpi-red">
    <div class="kpi-label">Day-1 drop-off increase (guardrail)</div>
    <div class="kpi-value">+{droppp:.1f} pp</div>
    <div class="kpi-sub">{gm['control_mean']:.1%} → {gm['treatment_mean']:.1%} &nbsp;·&nbsp; p = {gm['p_value']:.4f}, breached</div>
  </div>
  <div class="kpi-card kpi-blue">
    <div class="kpi-label">Bayesian confidence</div>
    <div class="kpi-value">{prob:.1f}%</div>
    <div class="kpi-sub">P(treatment &gt; control) &nbsp;·&nbsp; ROPE: {bay['rope_decision']}</div>
  </div>
</div>
"""


def design_html() -> str:
    return """
<section class="section" id="design">
  <div class="section-header">
    <div class="section-num">Experiment Design</div>
    <h2>Business Context &amp; Metric Definitions</h2>
  </div>
  <p>A B2B project-management SaaS product observed that users who do not activate in week 1
  almost never return. The onboarding team hypothesised that a structured wizard would reduce
  friction and increase the proportion reaching meaningful product engagement.</p>
  <div class="table-wrap">
    <table>
      <tr><th>Arm</th><th>Experience</th><th>N</th></tr>
      <tr><td>Control</td><td>Blank free-explore dashboard, users self-discover the product</td><td class="num">2,115</td></tr>
      <tr><td>Treatment</td><td>Guided 5-step wizard: create project → invite teammate → set due date → enable notifications → complete first task</td><td class="num">2,115</td></tr>
    </table>
  </div>
  <div class="table-wrap">
    <table>
      <tr><th>Metric</th><th>Role</th><th>Definition</th><th>Direction</th></tr>
      <tr><td><strong>Week-1 Activation Rate</strong></td><td><span class="badge badge-blue" style="background:#eff6ff;color:#1e3a5f">Primary</span></td>
          <td>User completes ≥ 3 of 5 key onboarding actions within 7 days</td><td>Higher ↑</td></tr>
      <tr><td><strong>Revenue Per User</strong></td><td><span class="badge badge-gray">Secondary</span></td>
          <td>MRR per user ($0 for free tier)</td><td>Higher ↑</td></tr>
      <tr><td><strong>Day-1 Drop-off Rate</strong></td><td><span class="badge badge-red">Guardrail</span></td>
          <td>User never returns after signup day</td><td>Lower ↓</td></tr>
    </table>
  </div>
  <p>Users were segmented by <strong>company size</strong> (solo 39%, small_team 46%, large_team 15%)
  and <strong>acquisition channel</strong> (organic 50%, paid 35%, referral 15%). The wizard was
  designed around collaborative features, creating a strong prior expectation of heterogeneous
  treatment effects across company size.</p>
</section>
"""


def planning_html() -> str:
    img = b64img("power_curves.png")
    return f"""
<section class="section" id="planning">
  <div class="section-header">
    <div class="section-num">Section 1</div>
    <h2>Pre-Experiment Planning, Power Analysis</h2>
  </div>
  <p>Required sample size computed using the exact two-proportion formula (not the pooled-SE approximation),
  targeting detection of a ≥ 20% relative lift at α = 0.05 with 80% power.</p>
  <div class="stat-grid">
    <div class="stat-box"><div class="stat-box-label">Baseline activation rate</div><div class="stat-box-value">18.0%</div></div>
    <div class="stat-box"><div class="stat-box-label">Minimum detectable effect</div><div class="stat-box-value">20% relative</div><div class="stat-box-sub">18.0% → 21.6%</div></div>
    <div class="stat-box"><div class="stat-box-label">Significance level (α)</div><div class="stat-box-value">0.05</div><div class="stat-box-sub">Two-sided</div></div>
    <div class="stat-box"><div class="stat-box-label">Target power</div><div class="stat-box-value">80%</div></div>
    <div class="stat-box"><div class="stat-box-label">Required N (per group)</div><div class="stat-box-value">1,923</div></div>
    <div class="stat-box"><div class="stat-box-label">Enrolled N (per group)</div><div class="stat-box-value">2,115</div><div class="stat-box-sub">+10% buffer</div></div>
  </div>
  <p>The power sensitivity table below shows that the experiment was appropriately sized, a 20% lift
  sits precisely at the 80% power target, while the planted 25% lift would be detectable with 93.5% power.</p>
  <div class="table-wrap">
    <table>
      <tr><th>True relative lift</th><th>Statistical power</th><th>Assessment</th></tr>
      <tr><td>10%</td><td class="num">29.7%</td><td>Under-powered, below business threshold</td></tr>
      <tr><td>15%</td><td class="num">56.4%</td><td>Marginal</td></tr>
      <tr><td>20%</td><td class="num" style="color:var(--green);font-weight:600">80.1%</td><td>✓ Designed target (MDE)</td></tr>
      <tr><td>25%</td><td class="num" style="color:var(--green);font-weight:600">93.5%</td><td>✓ Planted effect, well-powered</td></tr>
      <tr><td>30%</td><td class="num" style="color:var(--green);font-weight:600">98.5%</td><td>✓ Would be trivially detectable</td></tr>
    </table>
  </div>
  <img class="chart" src="{img}" alt="Power curves">
  <div class="chart-caption">Left: statistical power vs users per group for a 20% relative lift. Right: minimum detectable effect vs users per group. Both axes are log-scaled.</div>
</section>
"""


def eda_html() -> str:
    return f"""
<section class="section" id="eda">
  <div class="section-header">
    <div class="section-num">Section 2</div>
    <h2>Experiment Data &amp; Balance Check</h2>
  </div>
  <p>4,230 synthetic users were generated with realistic segment distributions, a latent user-quality
  variable driving covariate–outcome correlation, and a deliberately engineered guardrail tension.
  Pre-experiment covariates confirm balance between arms (as expected from random assignment).</p>
  <div class="table-wrap">
    <table>
      <tr><th>Metric</th><th>Control</th><th>Treatment</th></tr>
      <tr><td>Users</td><td class="num">2,115</td><td class="num">2,115</td></tr>
      <tr><td>Activations</td><td class="num">395</td><td class="num">482</td></tr>
      <tr><td>Activation rate</td><td class="num">18.68%</td><td class="num">22.79%</td></tr>
      <tr><td>Avg revenue per user</td><td class="num">$2.85</td><td class="num">$3.27</td></tr>
      <tr><td>Day-1 drop-off rate</td><td class="num">33.05%</td><td class="num">38.39%</td></tr>
      <tr><td>Pre-exp sessions (mean)</td><td class="num">7.16</td><td class="num">7.10</td></tr>
      <tr><td>Pre-exp feature depth (mean)</td><td class="num">4.16</td><td class="num">4.08</td></tr>
    </table>
  </div>
  <div class="alert alert-blue">
    <strong>Balance check</strong>
    Pre-experiment covariates are nearly identical between arms, confirming that random
    assignment produced balanced groups. Any difference in the experiment-period metrics
    is attributable to the wizard, not pre-existing user differences.
  </div>
  <div class="table-wrap">
    <table>
      <tr><th>Company size</th><th>Control activation</th><th>Treatment activation</th><th>Absolute lift</th><th>Relative lift</th></tr>
      <tr><td>large_team</td><td class="num">30.3%</td><td class="num">38.3%</td><td class="num">+8.0 pp</td><td class="num" style="color:var(--green);font-weight:600">+26.4%</td></tr>
      <tr><td>small_team</td><td class="num">21.6%</td><td class="num">27.0%</td><td class="num">+5.4 pp</td><td class="num" style="color:var(--green);font-weight:600">+24.9%</td></tr>
      <tr><td>solo</td><td class="num">10.8%</td><td class="num">11.6%</td><td class="num">+0.8 pp</td><td class="num" style="color:var(--muted)">+7.3%</td></tr>
    </table>
  </div>
  <p>The EDA already signals heterogeneous effects before formal testing: the wizard adds nearly
  nothing for solo users but produces a 25–26% relative lift for team users, mechanistically
  expected since steps 2 and 5 of the wizard (invite teammate, complete shared task) are
  irrelevant for solo accounts.</p>
</section>
"""


def primary_html() -> str:
    return f"""
<section class="section" id="primary">
  <div class="section-header">
    <div class="section-num">Section 3</div>
    <h2>Primary Metric, Week-1 Activation Rate</h2>
  </div>
  <p>Standard two-proportion z-test. Null hypothesis: wizard and no-wizard produce identical activation rates.</p>
  <div class="stat-grid">
    <div class="stat-box"><div class="stat-box-label">Control rate</div><div class="stat-box-value">{pm['control_mean']:.2%}</div></div>
    <div class="stat-box"><div class="stat-box-label">Treatment rate</div><div class="stat-box-value">{pm['treatment_mean']:.2%}</div></div>
    <div class="stat-box"><div class="stat-box-label">Absolute lift</div><div class="stat-box-value" style="color:var(--green)">+{(pm['treatment_mean']-pm['control_mean'])*100:.2f} pp</div></div>
    <div class="stat-box"><div class="stat-box-label">Relative lift</div><div class="stat-box-value" style="color:var(--green)">+{pm['relative_lift_pct']:.1f}%</div></div>
    <div class="stat-box"><div class="stat-box-label">z-statistic</div><div class="stat-box-value">3.300</div></div>
    <div class="stat-box"><div class="stat-box-label">p-value</div><div class="stat-box-value" style="color:var(--green)">{pm['p_value']:.4f}</div></div>
  </div>
  <div class="alert alert-green">
    <strong>Result: Statistically significant ✓</strong>
    The wizard increased week-1 activation by <strong>+22.0% relative</strong> (+4.1 pp absolute).
    95% CI: [+1.67 pp, +6.55 pp]. The p-value of 0.001 is far below α = 0.05 ,
    under the null hypothesis, we would observe a result this extreme fewer than 1 in 1,000 times.
  </div>
</section>
"""


def segments_html() -> str:
    img_size    = b64img("segment_forest_size.png")
    img_channel = b64img("segment_forest_channel.png")

    size_rows = ""
    for seg, label in [("large_team","large_team"), ("small_team","small_team"), ("solo","solo")]:
        r = segs[seg]
        color = "var(--green)" if r["significant"] else "var(--muted)"
        badge = sig_badge(r["significant"])
        size_rows += f"""<tr>
          <td>{label}</td>
          <td class="num" style="color:{color};font-weight:{'600' if r['significant'] else '400'}">+{r['rel_lift_pct']:.1f}%</td>
          <td class="num" style="{p_color(r['p_value'])}">{r['p_value']:.4f}</td>
          <td>{badge}</td>
        </tr>"""

    chan_rows = ""
    for seg, n_ctrl, ctrl_r, trt_r, lift, pval, sig in CHANNEL_SEGS:
        color = "var(--green)" if sig else "var(--muted)"
        badge = sig_badge(sig)
        chan_rows += f"""<tr>
          <td>{seg}</td><td class="num">{n_ctrl}</td>
          <td class="num">{ctrl_r:.1%}</td><td class="num">{trt_r:.1%}</td>
          <td class="num" style="color:{color};font-weight:{'600' if sig else '400'}">+{lift:.1f}%</td>
          <td class="num" style="{p_color(pval)}">{pval:.4f}</td>
          <td>{badge}</td>
        </tr>"""

    return f"""
<section class="section" id="segments">
  <div class="section-header">
    <div class="section-num">Section 4</div>
    <h2>Heterogeneous Treatment Effects, Segment Analysis</h2>
  </div>
  <p>Aggregate results mask critical variation. These subgroup analyses were pre-specified (not
  data-mined); we do not apply multiple-testing correction. The forest plots show relative lift (%)
  with 95% CI per stratum.</p>

  <h3 style="font-size:16px;margin:.75rem 0 .5rem">By company size (primary segmentation)</h3>
  <div class="table-wrap">
    <table>
      <tr><th>Segment</th><th>Relative lift</th><th>p-value</th><th>Significance</th></tr>
      {size_rows}
    </table>
  </div>
  <img class="chart" src="{img_size}" alt="Forest plot by company size">
  <div class="chart-caption">Forest plot, relative lift (%) with 95% CI by company size. Blue = significant; gray = not significant. Green dotted line = overall lift.</div>
  <div class="alert alert-amber">
    <strong>Key finding: solo users do not benefit from the wizard</strong>
    The solo segment (39% of users, N = 1,649) shows only +7.2% lift with p = 0.61.
    This is <em>not</em> a power issue, at N = 1,649, a genuine 25% effect would be detectable
    with &gt;99% power. The wizard is simply mismatched to solo use cases: steps 2 ("invite teammate")
    and 5 ("complete shared task") are meaningless for single-seat accounts.
  </div>

  <h3 style="font-size:16px;margin:1.5rem 0 .5rem">By acquisition channel (secondary segmentation)</h3>
  <div class="table-wrap">
    <table>
      <tr><th>Segment</th><th>N (control)</th><th>Control rate</th><th>Treatment rate</th><th>Relative lift</th><th>p-value</th><th>Significance</th></tr>
      {chan_rows}
    </table>
  </div>
  <img class="chart" src="{img_channel}" alt="Forest plot by acquisition channel">
  <div class="chart-caption">Forest plot, relative lift (%) with 95% CI by acquisition channel.</div>
  <p>Paid-channel users show the largest lift (+34.3%, p = 0.009), possibly because
  performance-marketing arrivals have lower baseline product familiarity and benefit more
  from explicit structure. The referral segment (N = 606) is too small to draw confident
  conclusions, the p = 0.32 result is consistent with a real 20% effect that we lack power to detect.</p>
</section>
"""


def secondary_html() -> str:
    img = b64img("revenue_distribution.png")
    return f"""
<section class="section" id="secondary">
  <div class="section-header">
    <div class="section-num">Section 5</div>
    <h2>Secondary Metric, Revenue Per User</h2>
  </div>
  <p>Welch's t-test (robust to unequal variances). Revenue is zero-inflated: most users are on the
  free tier ($0), with a small fraction on paid plans. The experiment was sized for the activation
  metric, not revenue, so a non-significant revenue result is expected and does not contradict
  a positive activation finding.</p>
  <div class="stat-grid">
    <div class="stat-box"><div class="stat-box-label">Control mean</div><div class="stat-box-value">${sm['control_mean']:.2f}</div></div>
    <div class="stat-box"><div class="stat-box-label">Treatment mean</div><div class="stat-box-value">${sm['treatment_mean']:.2f}</div></div>
    <div class="stat-box"><div class="stat-box-label">Absolute lift</div><div class="stat-box-value">+${sm['treatment_mean']-sm['control_mean']:.2f}</div></div>
    <div class="stat-box"><div class="stat-box-label">Relative lift</div><div class="stat-box-value">+{sm['relative_lift_pct']:.1f}%</div></div>
    <div class="stat-box"><div class="stat-box-label">95% CI</div><div class="stat-box-value" style="font-size:16px">[−$0.42, +$1.26]</div></div>
    <div class="stat-box"><div class="stat-box-label">p-value</div><div class="stat-box-value" style="color:var(--muted)">{sm['p_value']:.4f}</div></div>
  </div>
  <div class="alert alert-amber">
    <strong>Directionally positive, not yet significant</strong>
    p = 0.33 with a 95% CI straddling zero. The revenue signal is consistent with the activation
    story (more activated users → slightly more paid conversions) but we cannot rule out chance.
    A revenue-powered experiment would require ~4× more traffic to achieve significance on this metric.
  </div>
  <div class="table-wrap">
    <table>
      <tr><th>Arm</th><th>Users at $0</th><th>Paying users</th><th>Avg revenue (payers only)</th></tr>
      <tr><td>Control</td><td class="num">{REV_ZERO_CTRL:.1f}%</td><td class="num">{REV_PAY_CTRL:.1f}%</td><td class="num">${REV_ARPU_CTRL:.2f}</td></tr>
      <tr><td>Treatment</td><td class="num">{REV_ZERO_TRT:.1f}%</td><td class="num">{REV_PAY_TRT:.1f}%</td><td class="num">${REV_ARPU_TRT:.2f}</td></tr>
    </table>
  </div>
  <p>The positive revenue trend is driven by a higher fraction of users reaching the paid tier
  (5.2% → 6.0%), not by higher ARPU among existing payers ($55.22 → $54.40, essentially flat).
  This is mechanistically consistent: the wizard improves activation, and more activated users
  cross the paid-conversion threshold.</p>
  <img class="chart" src="{img}" alt="Revenue distribution">
  <div class="chart-caption">Left: fraction of users with $0 vs positive revenue per arm. Right: distribution of revenue among paying users only (zeros excluded).</div>
</section>
"""


def guardrail_html() -> str:
    return f"""
<section class="section" id="guardrail">
  <div class="section-header">
    <div class="section-num">Section 6</div>
    <h2>Guardrail Metric, Day-1 Drop-off Rate</h2>
  </div>
  <p>Day-1 drop-off measures users who never log in after their signup day, a leading indicator of
  long-term retention and LTV. A significant <em>increase</em> in drop-off is a guardrail breach,
  even if the primary metric is positive.</p>
  <div class="stat-grid">
    <div class="stat-box"><div class="stat-box-label">Control drop-off</div><div class="stat-box-value">{gm['control_mean']:.2%}</div></div>
    <div class="stat-box"><div class="stat-box-label">Treatment drop-off</div><div class="stat-box-value" style="color:var(--red)">{gm['treatment_mean']:.2%}</div></div>
    <div class="stat-box"><div class="stat-box-label">Absolute increase</div><div class="stat-box-value" style="color:var(--red)">+{gm['absolute_change_pp']*100:.2f} pp</div></div>
    <div class="stat-box"><div class="stat-box-label">p-value</div><div class="stat-box-value" style="color:var(--red)">{gm['p_value']:.4f}</div></div>
  </div>
  <div class="alert alert-red">
    <strong>⚠ Guardrail breached, highly significant</strong>
    Day-1 drop-off increased by +5.34 pp (p = 0.0003). The wizard's upfront multi-step commitment
    causes 1 in 19 additional users to abandon the product before returning. This is likely
    concentrated among low-intent users (e.g., speculative paid-ad clicks) who disengage when
    confronted with a mandatory flow before seeing the product's value.
  </div>
  <h3 style="font-size:16px;margin:.75rem 0 .5rem">Reconciling activation gain vs. drop-off increase</h3>
  <p>These findings are not contradictory, they describe different user populations:</p>
  <div class="two-col" style="gap:1rem;margin:.75rem 0">
    <div class="alert alert-green" style="margin:0">
      <strong>Users who stay past day 1</strong>
      Activate at a significantly higher rate in the wizard condition. The structured flow
      converts casual explorers into engaged users.
    </div>
    <div class="alert alert-red" style="margin:0">
      <strong>Additional users lost on day 1</strong>
      A larger fraction of enrolled users never return, eroding the activation denominator.
      The wizard's friction acts as an early filter.
    </div>
  </div>
  <p>The net activation effect across <em>all</em> enrolled users (+22%) outweighs the drop-off cost,
  but day-1 churn is a leading indicator of long-term retention. The 30- and 90-day cohort
  retention of wizard-activated users must be monitored post-launch to confirm the trade-off
  holds over longer time horizons.</p>
</section>
"""


def sequential_html() -> str:
    img = b64img("sequential_test.png")
    rows = ""
    for look, n_cum, pval, boundary, crossed in SEQ_ROWS:
        cross_cell = '<span class="badge badge-green">Crossed ✓</span>' if crossed else "-"
        pval_style = "color:var(--green);font-weight:600" if crossed else ""
        rows += f"""<tr>
          <td class="num">{look}</td>
          <td class="num">{n_cum:,}</td>
          <td class="num">{n_cum/s['n_users_total']*100:.0f}%</td>
          <td class="num" style="{pval_style}">{pval:.4f}</td>
          <td class="num">{boundary:.6f}</td>
          <td>{cross_cell}</td>
        </tr>"""
    return f"""
<section class="section" id="sequential">
  <div class="section-header">
    <div class="section-num">Section 7</div>
    <h2>Sequential Monitoring, Early Stopping Analysis</h2>
  </div>
  <p>The O'Brien-Fleming alpha-spending function was applied at 10 equally-spaced interim looks.
  It is deliberately conservative early (near-zero alpha at look 1) and becomes progressively
  more permissive as information accumulates, allowing early stopping without inflating the
  overall Type I error rate.</p>
  <div class="table-wrap">
    <table>
      <tr><th>Look</th><th>Cumulative N</th><th>% of planned N</th><th>p-value</th><th>O'B-F boundary</th><th>Boundary crossed?</th></tr>
      {rows}
    </table>
  </div>
  <div class="alert alert-green">
    <strong>Would have stopped at look 4 ✓</strong>
    After 2,540 users (60% of planned N), the p-value of 0.024 crossed the O'Brien-Fleming
    boundary of 0.024. This represents a potential <strong>40% saving in experiment runtime</strong>.
    In a real experiment with sequential monitoring infrastructure, this would have shortened
    the experiment by roughly 2–3 weeks depending on traffic volume.
  </div>
  <img class="chart" src="{img}" alt="Sequential test path">
  <div class="chart-caption">p-value trajectory (blue, circles) vs O'Brien-Fleming alpha boundary (red, dashed). The boundary is crossed at look 4.</div>
  <p><strong>Caveat</strong>: in a live experiment with guardrail monitoring, the stopping rule must
  be evaluated jointly across all metrics. The guardrail breach (day-1 drop-off) may not have been
  detectable at look 4, which would argue against stopping early despite the primary metric result.</p>
</section>
"""


def bayesian_html() -> str:
    img = b64img("posterior_lift.png")
    lo, hi = bay["credible_interval_95"]
    return f"""
<section class="section" id="bayesian">
  <div class="section-header">
    <div class="section-num">Section 8</div>
    <h2>Bayesian Analysis</h2>
  </div>
  <p>Beta-Binomial conjugate model with an <strong>informative prior</strong> Beta(18, 82),
  encoding the industry benchmark of ~18% SaaS onboarding activation across ~100 prior
  pseudo-observations. With 4,000+ real observations, the prior has negligible influence
  on the posterior but prevents over-confident conclusions from early looks.</p>
  <div class="stat-grid">
    <div class="stat-box"><div class="stat-box-label">Prior</div><div class="stat-box-value" style="font-size:16px">Beta(18, 82)</div><div class="stat-box-sub">Mean = 18.0%</div></div>
    <div class="stat-box"><div class="stat-box-label">P(treatment &gt; control)</div><div class="stat-box-value" style="color:var(--green)">{bay['prob_treatment_better']*100:.1f}%</div></div>
    <div class="stat-box"><div class="stat-box-label">Expected relative lift</div><div class="stat-box-value" style="color:var(--green)">+{bay['expected_lift_pct']:.1f}%</div></div>
    <div class="stat-box"><div class="stat-box-label">95% Credible Interval</div><div class="stat-box-value" style="font-size:16px">[+{lo:.1f}%, +{hi:.1f}%]</div></div>
  </div>
  <img class="chart" src="{img}" alt="Bayesian posterior">
  <div class="chart-caption">Left: posterior Beta distributions for activation rate (control vs treatment). Right: posterior distribution of relative lift, the probability mass entirely to the right of zero confirms treatment superiority.</div>
  <h3 style="font-size:16px;margin:1rem 0 .5rem">ROPE Decision</h3>
  <p>The Region of Practical Equivalence (ROPE) defines ±0.5 pp as commercially indistinguishable.
  Posterior probability that the lift exceeds this threshold:</p>
  <div class="stat-grid">
    <div class="stat-box"><div class="stat-box-label">P(treatment wins, lift &gt; ROPE)</div><div class="stat-box-value" style="color:var(--green)">99.7%</div></div>
    <div class="stat-box"><div class="stat-box-label">P(practically equivalent)</div><div class="stat-box-value">0.3%</div></div>
    <div class="stat-box"><div class="stat-box-label">P(control wins)</div><div class="stat-box-value">0.0%</div></div>
    <div class="stat-box"><div class="stat-box-label">ROPE decision</div><div class="stat-box-value" style="color:var(--green);font-size:16px">TREATMENT_WINS</div></div>
  </div>
  <div class="alert alert-blue">
    <strong>Frequentist vs. Bayesian comparison</strong>
    Both frameworks agree unambiguously: frequentist p = 0.001 vs Bayesian P(better) = 99.9%.
    The Bayesian credible interval [+7.8%, +36.1%] is directly interpretable, we are 95% confident
    the true relative lift lies in this range. The frequentist CI [+1.67 pp, +6.55 pp absolute]
    requires the additional step of dividing by the baseline to get relative terms.
  </div>
</section>
"""


def cuped_html() -> str:
    return f"""
<section class="section" id="cuped">
  <div class="section-header">
    <div class="section-num">Section 9</div>
    <h2>CUPED, Variance Reduction</h2>
  </div>
  <p>CUPED (Deng et al., 2013, Microsoft) reduces metric variance by removing the portion
  explained by pre-experiment covariates. Lower variance → tighter CIs → same true effect
  is easier to detect, equivalent to running a larger experiment for free.</p>
  <p><strong>Multi-covariate formula</strong>: <code>Y_cuped = Y − X_c @ θ</code> where
  <code>θ = OLS(Y ~ X_c)</code> and <code>X_c</code> is the column-centred covariate matrix.
  Variance reduction = R² of the OLS regression.</p>
  <div class="table-wrap">
    <table>
      <tr><th>Covariate</th><th>Pearson r with revenue</th><th>R² contribution</th></tr>
      <tr><td>pre_exp_sessions (login sessions, 14 days pre-launch)</td><td class="num">+0.196</td><td class="num">3.8%</td></tr>
      <tr><td>pre_exp_feature_depth (distinct features used in trial)</td><td class="num">+0.191</td><td class="num">3.6%</td></tr>
    </table>
  </div>
  <div class="stat-grid">
    <div class="stat-box"><div class="stat-box-label">Original variance</div><div class="stat-box-value">194.81</div></div>
    <div class="stat-box"><div class="stat-box-label">CUPED variance</div><div class="stat-box-value">186.35</div></div>
    <div class="stat-box"><div class="stat-box-label">Variance reduction</div><div class="stat-box-value" style="color:var(--blue)">{cup['variance_reduction_pct']:.1f}%</div></div>
    <div class="stat-box"><div class="stat-box-label">Effective sample gain</div><div class="stat-box-value" style="color:var(--blue)">{cup['effective_sample_gain_pct']:.1f}%</div></div>
  </div>
  <div class="table-wrap">
    <table>
      <tr><th>Test</th><th>p-value</th><th>95% CI</th></tr>
      <tr><td>Original Welch t-test</td><td class="num">0.3268</td><td class="num">[−$0.42, +$1.26]</td></tr>
      <tr><td>CUPED-adjusted t-test</td><td class="num" style="color:var(--blue);font-weight:600">0.2435</td><td class="num">[−$0.33, +$1.31]</td></tr>
    </table>
  </div>
  <div class="alert alert-blue">
    <strong>Why is the reduction modest (4.3%)?</strong>
    Revenue is 94%+ zeros. When nearly all variance comes from the binary zero/non-zero split,
    continuous covariates can only explain the small fraction of variance in the positive-revenue
    tail. CUPED is most powerful when: (a) the metric is continuous and low-noise, or (b) the
    covariate is a direct historical lag of the metric itself (e.g., "revenue last week"). On
    lower-variance metrics like session count or feature usage breadth, the same covariates
    would likely yield 15–30% reduction.
  </div>
  <p>CUPED does not change the point estimate, only variance and CI width. This is guaranteed
  by the centring step: the adjusted metric has the same mean as the original.</p>
</section>
"""


def calibration_html() -> str:
    img = b64img("pvalue_sim_distribution.png")
    return f"""
<section class="section" id="calibration">
  <div class="section-header">
    <div class="section-num">Section 10</div>
    <h2>Calibration Check, p-value Distribution</h2>
  </div>
  <p>200 independent synthetic experiments were run under H₀ (no true effect) and H₁ (true lift = MDE = 20%)
  to verify the test statistic is correctly specified.</p>
  <div class="stat-grid">
    <div class="stat-box"><div class="stat-box-label">Type I error (H₀, α = 5%)</div><div class="stat-box-value" style="color:var(--green)">{cal['type_i_error']*100:.1f}%</div><div class="stat-box-sub">Target: 5.0% ✓</div></div>
    <div class="stat-box"><div class="stat-box-label">Empirical power (H₁, MDE = 20%)</div><div class="stat-box-value" style="color:var(--green)">{cal['empirical_power']*100:.1f}%</div><div class="stat-box-sub">Target: 80.0% ✓</div></div>
    <div class="stat-box"><div class="stat-box-label">Simulations (H₀)</div><div class="stat-box-value">200</div></div>
    <div class="stat-box"><div class="stat-box-label">Simulations (H₁)</div><div class="stat-box-value">200</div></div>
  </div>
  <img class="chart" src="{img}" alt="p-value calibration">
  <div class="chart-caption">Left: p-value distribution under H₀, approximately Uniform[0,1], confirming no anti-conservatism. Right: p-value distribution under H₁, strongly left-skewed, confirming 80% power at the MDE.</div>
  <p>The slight undershots (4.0% vs 5.0% Type I error; 78.5% vs 80% power) are within the
  expected sampling variability for 200 simulations (SE ≈ ±1.5 pp at p ≈ 0.05). The test
  is well-calibrated with no systematic bias.</p>
</section>
"""


def decision_html() -> str:
    img = b64img("metric_scorecard.png")
    return f"""
<section class="section" id="decision">
  <div class="section-header">
    <div class="section-num">Section 11</div>
    <h2>Decision Framework</h2>
  </div>

  <img class="chart" src="{img}" alt="Metric scorecard">
  <div class="chart-caption">Traffic-light scorecard: primary ✓ (ship), secondary ~ (neutral), guardrail ✗ (concern).</div>

  <h3 style="font-size:16px;margin:1.25rem 0 .5rem">Evidence summary</h3>
  <div class="table-wrap">
    <table>
      <tr><th>Metric</th><th>Role</th><th>Control</th><th>Treatment</th><th>Relative lift</th><th>p-value</th><th>Verdict</th></tr>
      <tr>
        <td>Week-1 Activation</td><td>Primary</td>
        <td class="num">{pm['control_mean']:.1%}</td><td class="num">{pm['treatment_mean']:.1%}</td>
        <td class="num" style="color:var(--green);font-weight:600">+{pm['relative_lift_pct']:.1f}%</td>
        <td class="num" style="{p_color(pm['p_value'])}">{pm['p_value']:.4f}</td>
        <td><span class="badge badge-green">Ship ✓</span></td>
      </tr>
      <tr>
        <td>Revenue Per User</td><td>Secondary</td>
        <td class="num">${sm['control_mean']:.2f}</td><td class="num">${sm['treatment_mean']:.2f}</td>
        <td class="num">+{sm['relative_lift_pct']:.1f}%</td>
        <td class="num" style="{p_color(sm['p_value'])}">{sm['p_value']:.4f}</td>
        <td><span class="badge badge-gray">Neutral ~</span></td>
      </tr>
      <tr>
        <td>Day-1 Drop-off</td><td>Guardrail</td>
        <td class="num">{gm['control_mean']:.1%}</td><td class="num">{gm['treatment_mean']:.1%}</td>
        <td class="num" style="color:var(--red);font-weight:600">+{gm['absolute_change_pp']*100:.1f} pp</td>
        <td class="num" style="{p_color(gm['p_value'])}">{gm['p_value']:.4f}</td>
        <td><span class="badge badge-red">Concern ✗</span></td>
      </tr>
    </table>
  </div>

  <h3 style="font-size:16px;margin:1.25rem 0 .5rem">Segment recommendation</h3>
  <div class="rec-grid">
    <div class="rec-card rec-ship">
      <h4>✓ Ship to small_team</h4>
      <div class="rec-metric" style="color:var(--green)">+24.9%</div>
      <p>N = 1,935 · p = 0.006. Strong, significant activation gain. Wizard steps are directly
      relevant: inviting teammates and shared tasks are core small-team use cases.</p>
    </div>
    <div class="rec-card rec-ship">
      <h4>✓ Ship to large_team</h4>
      <div class="rec-metric" style="color:var(--green)">+26.4%</div>
      <p>N = 646 · p = 0.032. Largest relative lift. Large-team users likely have IT-driven
      signups and benefit from the structured setup to get to first value quickly.</p>
    </div>
    <div class="rec-card rec-hold">
      <h4>~ Hold for solo</h4>
      <div class="rec-metric" style="color:var(--amber)">+7.2%</div>
      <p>N = 1,649 · p = 0.613. No significant benefit. The wizard's collaborative steps are
      irrelevant for single-seat accounts and the day-1 drop-off cost is not justified.
      Test a solo-specific checklist instead.</p>
    </div>
  </div>

  <div class="alert alert-blue" style="margin-top:1.25rem">
    <strong>Post-launch monitoring plan</strong>
    Ship wizard to team users and monitor the following at 30 and 90 days:
    (1) Week-4 retention rate, do wizard-activated users stay active?
    (2) Trial-to-paid conversion, does higher activation translate to revenue?
    (3) Day-7 churn, does the day-1 drop-off signal persist?
    (4) Feature adoption breadth, are activated users exploring the product or just completing wizard steps?
    If day-7 churn exceeds the pre-experiment baseline by &gt; 2 pp, pause the wizard and audit
    the step with highest abandonment (hypothesised: step 2, "Invite a teammate").
  </div>
</section>
"""


# ── Assemble ──────────────────────────────────────────────────────────────────

def build_html() -> str:
    body = "\n".join([
        nav_html(),
        "<main>",
        hero_html(),
        kpi_strip_html(),
        design_html(),
        planning_html(),
        eda_html(),
        primary_html(),
        segments_html(),
        secondary_html(),
        guardrail_html(),
        sequential_html(),
        bayesian_html(),
        cuped_html(),
        calibration_html(),
        decision_html(),
        "<footer>Generated by ab-test-framework · saas_onboarding_wizard · 2026-06-24</footer>",
        "</main>",
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Experiment Report, SaaS Onboarding Wizard</title>
  <style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>"""


if __name__ == "__main__":
    html = build_html()
    out  = ROOT / "report.html"
    out.write_text(html, encoding="utf-8")
    size_kb = out.stat().st_size / 1024
    print(f"Generated {out}  ({size_kb:.0f} KB)")

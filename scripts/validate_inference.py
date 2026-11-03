"""Predefined fixed-horizon calibration; sequential recommendations disabled."""
from pathlib import Path
import sys,json,hashlib,importlib.metadata
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from scipy import stats
from src.abtest.power import required_sample_size
from src.abtest.cuped import adjusted_effect
from src.abtest.frequentist import two_proportion_ztest,release_decision,segment_analysis,segment_interaction,welch_ttest
from src.abtest.simulate import generate_experiment
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs"
SEED=20261103
BINARY_SIMS=10000
ADJUSTED_SIMS=2000

def uncertainty(k,n):
    return [float(stats.beta.ppf(.025,k,n-k+1)) if k else 0.,float(stats.beta.ppf(.975,k+1,n-k)) if k<n else 1.]

def main():
    rng=np.random.default_rng(SEED);n=required_sample_size(.18,.2)
    binary=[]
    for delta in [0.,.018,.036,.054]:
        c=rng.binomial(n,.18,BINARY_SIMS);t=rng.binomial(n,.18+delta,BINARY_SIMS)
        pc=c/n;pt=t/n;pool=(c+t)/(2*n);se=np.sqrt(pool*(1-pool)*2/n)
        pvals=2*stats.norm.sf(abs((pt-pc)/se))
        se_ci=np.sqrt(pc*(1-pc)/n+pt*(1-pt)/n)
        covered=(pt-pc-1.96*se_ci<=delta)&(pt-pc+1.96*se_ci>=delta)
        k=int((pvals<.05).sum())
        binary.append({"delta":delta,"n_per_arm":n,"simulations":BINARY_SIMS,"rejection_rate":k/BINARY_SIMS,"rejection_interval":uncertainty(k,BINARY_SIMS),"ci_coverage":float(covered.mean()),"expected_total_sample":2*n})
    adjusted=[]
    for imbalance in [0.,.75]:
      for skew in [False,True]:
       for effect in [0.,.2]:
        estimates=[];cover=[];reject=[];ses=[];rawses=[]
        for _ in range(ADJUSTED_SIMS):
            t=np.repeat([0,1],300);x=rng.normal(size=600)+imbalance*t
            noise=(rng.lognormal(0,.8,600)-np.exp(.8**2/2)) if skew else rng.normal(size=600)
            y=effect*t+1.5*x+noise
            frame=pd.DataFrame({"variant":np.where(t,"treatment","control"),"x":x,"y":y})
            r=adjusted_effect(frame,"y",["x"])
            estimates.append(r["estimate"]);ses.append(r["se"]);cover.append(r["ci_lower"]<=effect<=r["ci_upper"]);reject.append(r["p_value"]<.05)
            rawses.append(np.sqrt(y[t==0].var(ddof=1)/300+y[t==1].var(ddof=1)/300))
        k=sum(cover);rejections=sum(reject)
        adjusted.append({"covariate_mean_shift":imbalance,"skewed_noise":skew,"true_effect":effect,"simulations":ADJUSTED_SIMS,"bias":float(np.mean(estimates)-effect),"coverage":k/ADJUSTED_SIMS,"coverage_interval":uncertainty(k,ADJUSTED_SIMS),"rejection_rate":rejections/ADJUSTED_SIMS,"rejection_interval":uncertainty(rejections,ADJUSTED_SIMS),"mean_se":float(np.mean(ses)),"raw_mean_se":float(np.mean(rawses))})
    passed=(.035<binary[0]["rejection_rate"]<.065 and .77<binary[2]["rejection_rate"]<.83 and all(.925<r["coverage"]<.975 and abs(r["bias"])<.03 for r in adjusted))
    result={"seed":SEED,"status":"passed" if passed else "failed","binary":binary,"adjusted":adjusted,"acceptance":"Null rejection .035..065; planned MDE power .77..83; adjusted coverage .925..975 and absolute bias below .03. Chosen before simulation.","sequential":"disabled, no stopping claims","scope":"Binary independent Bernoulli at baseline .18 and planned n; adjusted additive linear outcomes with normal or centered lognormal errors; no arbitrary heavy-tail or observational causal guarantee."}
    OUT.mkdir(exist_ok=True);(OUT/"inference_validation.json").write_text(json.dumps(result,indent=2)+"\n", newline="\n", encoding="utf-8")
    data=generate_experiment(4230,true_lift=.25,seed=42)
    c=data[data.variant=="control"];t=data[data.variant=="treatment"]
    primary=two_proportion_ztest(c.activated,t.activated);guardrail=two_proportion_ztest(c.day1_dropoff,t.day1_dropoff)
    summary={"primary":primary,"guardrail":guardrail,"revenue":welch_ttest(c.revenue,t.revenue),"release":release_decision(primary,guardrail,.02),"adjusted_revenue":adjusted_effect(data,"revenue",["pre_exp_sessions","pre_exp_feature_depth"]),"interactions":{name:segment_interaction(data,name,"activated") for name in ["company_size","acquisition_channel"]}}
    from statsmodels.stats.multitest import multipletests
    for key,p in zip(summary["interactions"],multipletests([r["p_value"] for r in summary["interactions"].values()],method="holm")[1]):summary["interactions"][key]["p_adjusted"]=float(p)
    (OUT/"run_summary.json").write_text(json.dumps(summary,indent=2)+"\n", newline="\n", encoding="utf-8")
    for name in ["company_size","acquisition_channel"]:segment_analysis(data,name,"activated").to_csv(OUT/f"segments_{name}.csv",index=False, lineterminator="\n")
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    inputs={p.relative_to(ROOT).as_posix():digest(p) for p in (ROOT/"src").rglob("*.py")};inputs["scripts/validate_inference.py"]=digest(Path(__file__))
    manifest={"status":result["status"],"inputs":inputs,"seed":SEED,"packages":{d.metadata["Name"]:d.version for d in importlib.metadata.distributions()},"outputs":{name:digest(OUT/name) for name in ["inference_validation.json","run_summary.json"]},"tolerance":"Seeded simulation frequencies exact with pinned stack; numerical coefficients absolute tolerance 1e-6."}
    (OUT/"inference_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n", newline="\n", encoding="utf-8")
    print(json.dumps(result,indent=2))
    if not passed:raise SystemExit("Calibration acceptance failed")

if __name__=="__main__":main()

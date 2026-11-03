import numpy as np
import pandas as pd
import pytest
from scipy import stats
from src.abtest.frequentist import sequential_test,two_proportion_ztest,release_decision,segment_interaction
from src.abtest.cuped import adjusted_effect


def test_early_stopping_disabled():
    with pytest.raises(NotImplementedError):sequential_test(pd.Series([0,1]),pd.Series([1,1]))


def test_binary_calibration_kernel_matches_public_reference():
    n=1923;rng=np.random.default_rng(7)
    for _ in range(50):
        c,t=rng.binomial(n,.18,2);pool=(c+t)/(2*n)
        expected=2*stats.norm.sf(abs((t/n-c/n)/np.sqrt(pool*(1-pool)*2/n)))
        actual=two_proportion_ztest(pd.Series(np.arange(n)<c),pd.Series(np.arange(n)<t))
        assert actual["p_value"]==pytest.approx(expected,abs=1e-6)


def test_covariate_adjustment_recovers_effect_under_mean_imbalance():
    rng=np.random.default_rng(4);t=np.repeat([0,1],2000);x=rng.normal(size=4000)+t
    df=pd.DataFrame({"variant":np.where(t,"treatment","control"),"x":x,"y":.2*t+2*x+rng.normal(size=4000)})
    result=adjusted_effect(df,"y",["x"])
    assert result["ci_lower"]<.2<result["ci_upper"]


def test_noninferiority_guardrail_requires_evidence():
    primary={"ci_lower":.01};uncertain={"ci_upper":.03}
    assert not release_decision(primary,uncertain,.02)["release"]
    assert release_decision(primary,{"ci_upper":.01},.02)["release"]

import numpy as np
import pandas as pd
from fastclime.m3_ml.models.stress_clf import StressClf


def test_stress_clf_tiny():
    X = pd.DataFrame(np.random.rand(200, 5), columns=list("abcde"))
    y = pd.Series((X.a > 0.5).astype(int))
    mdl, m = StressClf.train(X, y)
    assert m["roc_auc"] > 0.7

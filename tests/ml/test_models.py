import numpy as np
import pandas as pd
from fastclime.m3_ml.models.stress_clf import StressClf
from fastclime.m3_ml.models.lamina_reg import LaminaReg
from sklearn.metrics import r2_score


def test_stress_clf_tiny():
    X = pd.DataFrame(np.random.rand(200, 5), columns=list("abcde"))
    y = pd.Series((X.a > 0.5).astype(int))
    mdl, m = StressClf.train(X, y)
    assert m["roc_auc"] > 0.8


def test_lamina_reg_tiny():
    X = pd.DataFrame(np.random.rand(200, 5), columns=list("abcde"))
    # Create a linear relationship for y
    y = pd.Series(2 * X.a + 3 * X.b + np.random.randn(200) * 0.1)
    mdl, m = LaminaReg.train(X, y)
    preds = mdl.predict(X)
    assert r2_score(y, preds) > 0.7

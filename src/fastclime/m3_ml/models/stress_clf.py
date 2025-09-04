import lightgbm as lgb
from sklearn.metrics import roc_auc_score, f1_score
from .base import BaseModel


class StressClf(lgb.LGBMClassifier, BaseModel):
    @staticmethod
    def default_params():
        return dict(
            objective="binary",
            n_estimators=300,
            learning_rate=0.05,
            num_leaves=32,
            random_state=42,
        )

    @classmethod
    def train(cls, X, y, **kwargs):
        mdl = cls(**cls.default_params() | kwargs)
        mdl.fit(X, y)
        y_pred = mdl.predict_proba(X)[:, 1]
        metrics = dict(
            roc_auc=roc_auc_score(y, y_pred),
            f1=f1_score(y, y_pred > 0.5),
        )
        return mdl, metrics

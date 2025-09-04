import lightgbm as lgb
from sklearn.metrics import mean_squared_error, mean_absolute_error
from .base import BaseModel
import numpy as np


class LaminaReg(lgb.LGBMRegressor, BaseModel):
    @staticmethod
    def default_params():
        return dict(
            objective="regression_l1",
            n_estimators=300,
            learning_rate=0.05,
            num_leaves=32,
            random_state=42,
        )

    @classmethod
    def train(cls, X, y, **kwargs):
        mdl = cls(**cls.default_params() | kwargs)
        mdl.fit(X, y)
        y_pred = mdl.predict(X)
        metrics = dict(
            rmse=np.sqrt(mean_squared_error(y, y_pred)),
            mae=mean_absolute_error(y, y_pred),
        )
        return mdl, metrics

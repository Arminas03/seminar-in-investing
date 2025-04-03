from arch import arch_model
import pandas as pd
import numpy as np


def sigma_hat_rv(sum_sq_ret):
    return np.sqrt(sum_sq_ret * 21 / 126)


def garch_sigma_hat(monthly_returns_dict):
    dates = []
    rets = []

    for (year, month), ret in monthly_returns_dict.items():
        dt = pd.Timestamp(year=year, month=month, day=1)
        dates.append(dt)
        rets.append(ret)

    returns_series = pd.Series(rets, index=dates).sort_index()

    model = arch_model(
        returns_series, mean="Zero", vol="Garch", p=1, q=1, dist="normal"
    )
    fitted_model = model.fit(disp="off")

    forecast = fitted_model.forecast(horizon=1)
    next_period_var = forecast.variance.iloc[-1, 0]
    next_period_vol = np.sqrt(next_period_var)

    return fitted_model, next_period_vol

import pandas as pd
import numpy as np
from collections import defaultdict
import json


STRATEGY_COMPOSITIONS = [
    (strat, weight)
    for strat in ["standard", "hedged_rv", "hedged_garch"]
    for weight in ["equal", "value"]
]


def evaluate_strategy_performance(lbda, strategy, weight):
    gross_return_list, net_return_list, cost_list = [], [], []

    for start_year, end_year in [(1993, 2005), (2005, 2024)]:
        strategy_results = pd.read_csv(
            f"lambda_{lbda}_res/ret_cost_{strategy}_{weight}_{start_year}_{end_year}.csv"
        )

        if strategy_results.iloc[-1]["year"] > end_year:
            strategy_results = strategy_results.iloc[:-1]

        gross_return_list += list(strategy_results["total_return"])
        net_return_list += list(
            strategy_results["total_return"] - strategy_results["total_cost"]
        )

        cost_list += list(strategy_results["total_cost"])

    avg_gross_return = sum(gross_return_list) / len(gross_return_list)
    avg_net_return = sum(net_return_list) / len(net_return_list)
    gross_return_std = float(np.array(gross_return_list).std())
    net_return_std = float(np.array(net_return_list).std())

    return (
        avg_gross_return,
        gross_return_std,
        avg_net_return,
        net_return_std,
        gross_return_list,
        cost_list,
    )


def main():
    time_series_results = defaultdict()
    strategy_agg_results = defaultdict(lambda: defaultdict(dict))
    for lbda in [0, 1, 6, 12]:
        for strategy, weight in STRATEGY_COMPOSITIONS:
            (
                strat_return,
                strat_std,
                strat_net_return,
                strat_net_std,
                gross_returns,
                costs,
            ) = evaluate_strategy_performance(lbda, strategy, weight)
            strategy_agg_results[lbda][strategy][weight] = {
                "monthly_gross_return": strat_return,
                "monthly_gross_return_std": strat_std,
                "monthly_net_return": strat_net_return,
                "monthly_net_return_std": strat_net_std,
            }
            time_series_results[(lbda, strategy, weight, "gross_return")] = (
                gross_returns
            )
            time_series_results[(lbda, strategy, weight, "costs")] = costs

    with open("strategy_performances.json", "w") as file:
        json.dump(strategy_agg_results, file)
    pd.DataFrame(
        time_series_results,
        index=pd.date_range(start="1994-01", periods=(2024 - 1994 + 1) * 12, freq="ME"),
    ).to_csv("ret_cost_ts.csv", index=True, header=True)


if __name__ == "__main__":
    main()

import os
import pickle

import numpy as np

DIRNAME = os.path.dirname(__file__)


def main():
    """
    Generates forecast percentiles from full posterior and aggregated
    percentiles for the next 4 hours
    """

    # Reads in results
    results = pickle.load(
        open(os.path.join(DIRNAME, "../../../data/forecast_results.pkl"), "rb")
    )
    time = results["time"]
    posterior = results["posterior"]

    # Finds 5th, 50th and 95th percentiles of posterior
    percentiles = np.percentile(posterior, [5, 50, 95], axis=0)

    # Saves results to dict
    results_percentiles = {}
    results_percentiles["time"] = time
    results_percentiles["percentiles"] = percentiles

    pickle.dump(
        results_percentiles,
        open(os.path.join(DIRNAME, "forecast_percentiles.pkl"), "wb",),
    )

    # Aggregated percentiles for next 4 hours
    hours_ahead = 4

    # Finds index of last timestamp there are 4 hours ahead for
    idmax_datetime = len(time) - hours_ahead

    agg_percentiles_lower = []
    agg_percentiles_upper = []

    for id_datetime in range(0, idmax_datetime):

        # For each timestamp, finds sum of posterior across next 4 hours for
        # each sample
        posterior_sum = np.sum(
            posterior[:, id_datetime : id_datetime + hours_ahead], axis=1,
        )

        # Finds 5th and 95th percentile
        agg_percentiles_lower.append(
            int(round(np.percentile(posterior_sum, 5, axis=0,)))
        )
        agg_percentiles_upper.append(
            int(round(np.percentile(posterior_sum, 95, axis=0,)))
        )

    # Saves results to dict
    results_agg_percentiles = {}
    results_agg_percentiles["time"] = time[:idmax_datetime]
    results_agg_percentiles["lower"] = np.array(agg_percentiles_lower)
    results_agg_percentiles["upper"] = np.array(agg_percentiles_upper)

    pickle.dump(
        results_agg_percentiles,
        open(
            os.path.join(DIRNAME, "forecast_aggregated_percentiles.pkl",),
            "wb",
        ),
    )


if __name__ == "__main__":

    main()

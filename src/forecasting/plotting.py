import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from forecasting.utils import (
    load_timeseries,
    split_historic_forecast,
    split_training,
)


def ribbon_plot(
    x: np.ndarray,
    y: np.ndarray,
    n_ribbons: int = 10,
    percentile_min: int = 5,
    percentile_max: int = 95,
    ribbon_color: str = "r",
    plot_median: bool = True,
    line_color: str = "k",
    ax: plt.Axes = None,
    fill_kwargs=None,
    line_kwargs=None,
) -> plt.Axes:
    """
    Make a ribbon plot that shows the different quantiles of the
    distribution of y against x.

    Parameters
    ----------
    x: 1d array
        The values for the x axis
    y: 2d array
    n_ribbons: int (default 10)
        How many quantiles to show
    percentile_min: float, between 0 and 50
        The lowest percentile to be shown
    percentile_max: float between 50 and 100
        The highest percentile to show
    ribbon_color: str (default 'r')
        Color for the ribbons, must be a valid expression for
        matplotlib colors
    plot_median: bool (default True)
        Whether or not to plot a line for the 50% percentile
    line_color: str (default 'k')
        Color to use for the median
    ax: matplotlib.Axes
        Where to plot the figure
    fill_kwargs: dict
        Extra arguments passed to `plt.fill_between`, Controls the aspect of
        the ribbons
    line_kwargs: dict
        Extra arguments to be passed to `plt.plot`, controls the aspect of the
        median line

    Returns
    -------
    matplotlib.Axes
    """
    perc1 = np.percentile(
        y,
        np.linspace(percentile_min, 50, num=n_ribbons, endpoint=False),
        axis=0,
    )
    perc2 = np.percentile(
        y, np.linspace(50, percentile_max, num=n_ribbons + 1)[1:], axis=0
    )
    fill_kwargs = fill_kwargs or {}
    line_kwargs = line_kwargs or {}
    alpha = fill_kwargs.pop("alpha", 1 / n_ribbons)
    ax = ax or plt.gca()
    plt.sca(ax)

    # Fill ribbons
    for p1, p2 in zip(perc1, perc2):
        plt.fill_between(
            x, p1, p2, alpha=alpha, color=ribbon_color, **(fill_kwargs or {})
        )

    if plot_median:
        plot_func = plt.step if fill_kwargs.pop("step", None) else plt.plot
        plot_func(
            x, np.median(y, axis=0), color=line_color, **(line_kwargs or {})
        )

    return plt.gca()


def plot_forecast(
    date: pd.Timestamp, results: dict, historic_hours: int, forecast_hours: int
):
    """
    Plots the historic admissions data along with the forecast model
    prediction for past and future.

    Parameters
    ----------
    date: timestamp
        When forecast begins
    results: dict
        Output from PatientForecast.call_forecast method
    historic_hours: int
        Number of hours in the past for historic data and forecast to be
        plotted for
    forecast_hours: int
        Number of hours in the future for forecast to be plotted for
    """

    start = date - (pd.Timedelta("1H") * historic_hours)
    end = date + (pd.Timedelta("1H") * forecast_hours)
    ax_date_format = mdates.DateFormatter("%A %d\n%B")

    training_data = load_timeseries()
    training_ids = split_training(training_data.index, date, historic_hours)
    training_data = training_data.iloc[training_ids]

    times = results["time"]
    posterior = results["posterior"]

    historic_ids, forecast_ids = split_historic_forecast(
        times, date, historic_hours + 1, forecast_hours + 1
    )

    historic_ids += 1

    historic_times = times[historic_ids]
    historic_data = posterior[:, historic_ids]

    forecast_times = times[forecast_ids]
    forecast_data = posterior[:, forecast_ids]

    f, ax = plt.subplots(1, 1, figsize=(25, 5))
    ax.plot(
        training_data,
        marker="o",
        lw=0,
        label="Training data",
    )
    ribbon_plot(
        historic_times,
        historic_data,
        plot_median=False,
        ax=ax,
        ribbon_color="grey",
    )
    ribbon_plot(
        forecast_times,
        forecast_data,
        plot_median=False,
        ax=ax,
        ribbon_color="coral",
    )
    ax.axvline(x=date, linestyle="--", color="black")
    ax.xaxis.set_major_formatter(ax_date_format)
    ax.legend(loc=2)
    ax.set_ylabel("Hospital admissions per hour")
    ax.set_xlabel("Date")
    ax.set_xlim([start, end])

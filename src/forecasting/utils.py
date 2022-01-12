import os
from typing import Tuple

import numpy as np
import pandas as pd

DIRNAME = os.path.dirname(__file__)

START_FORECAST = pd.to_datetime("01/05/1855 00:00", dayfirst=True)
HISTORIC_HOURS = 168
FORECAST_HOURS = 24
HOURS_IN_WEEK = 168


def load_timeseries(freq: str = "H") -> pd.DataFrame:
    """Load in historic admissions data and preprocess."""

    try:
        df = pd.read_csv(
            os.path.join(DIRNAME, "../../data/historic_admissions.csv"),
            index_col=0,
        )
    except FileNotFoundError as e:
        print("Historic admissions data not found")
        raise e

    df = df[["ADMIT_DTTM", "Total"]]

    xy = _preprocess(df).resample(freq).sum().sort_index()

    return xy


def load_holidays() -> pd.DataFrame:
    """Load in historic bank holiday information."""

    # 2016 to 2022
    _holidays_2016_2022_json = pd.read_json(
        "https://www.gov.uk/bank-holidays.json"
    ).loc["events", "england-and-wales"]

    # 2015
    _holidays_2015_str = """
    New Year's Day	Thu, 1 Jan 2015
    Good Friday	Fri, 3 Apr 2015
    Easter Monday	Mon, 6 Apr 2015
    Early May Bank Holiday	Mon, 4 May 2015
    Spring Bank Holiday	Mon, 25 May 2015
    Christmas Day	Fri, 25 Dec 2015
    Boxing Day	Mon, 28 Dec 2015
    """

    holidays_2015 = pd.to_datetime(
        [line.split("\t")[1] for line in _holidays_2015_str.split("\n")[1:-1]],
        format="%a, %d %b %Y",
    )

    holidays_2016_2022 = pd.to_datetime(
        [entry["date"] for entry in _holidays_2016_2022_json]
    )
    holiday_dates = holidays_2015.union(holidays_2016_2022)

    holidays = holiday_dates.copy()

    return holidays


def _preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Change time to timestamp and set to index."""
    df.columns = ["time", "value"]
    df["time"] = pd.to_datetime(df["time"])
    y_full = df.set_index("time")["value"]
    return y_full


def map_to_date(day: str, hour: int) -> pd.Timestamp:
    """
    Maps day of the week and hour of the day to timestamp within week
    beginning at START_FORECAST.
    """

    week_window = pd.date_range(START_FORECAST, periods=168, freq="1H")

    week_days = week_window.day_name()
    week_hours = week_window.hour

    date_lookup = pd.DataFrame(
        data={
            "day": week_days.str.lower(),
            "hour": week_hours,
            "datetime": week_window,
        }
    )
    date_lookup.sort_values(by=["day", "hour"], inplace=True)
    date_lookup.set_index(["day", "hour"], inplace=True)

    date = pd.to_datetime(date_lookup.loc[(day.lower(), hour), :].values[0])

    return date


def split_historic_forecast(
    times: pd.DatetimeIndex,
    date: pd.Timestamp,
    historic_hours: int,
    forecast_hours: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Selects times in desired periods before and after start of forecast.

    Parameters
    ----------
    times: 1d array of timestamps
        Times forecast model has returned prediction for
    date: timestamp
        Start of forwards forecast
    historic_hours: int
        Number of hours in the past forecast needed for
    forecast_hours: int
        Number of hours in the future forecast needed for

    Returns
    -------
    historic_ids: 1d array
        Index values for times where timestamp is in historic_hours window
    forecast_hours: 1d array
        Index values for times where timestamp is in forecast_hours window
    """

    match = np.where(times == date)[0][0]

    historic_ids = np.arange(match - historic_hours, match)
    forecast_ids = np.arange(match, match + forecast_hours)

    return historic_ids, forecast_ids


def split_training(
    times: pd.DatetimeIndex, date: pd.Timestamp, training_hours: int
) -> np.ndarray:
    """
    Selects times in desired period before start of forecast.

    Parameters
    ----------
    times: 1d array of timestamps
        Times forecast model has returned prediction for
    date: timestamp
        Start of forwards forecast
    training_hours:
        Number of hours in the past training data needed for

    Returns
    -------
    training_ids: 1d array
        Index values for times where timestamp is in training_hours window
    """

    match = np.where(times == date)[0][0]

    training_ids = np.arange(match - training_hours, match)

    return training_ids

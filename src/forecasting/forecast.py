import os

import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import pandas as pd
from numpyro.infer import MCMC, NUTS, Predictive, init_to_median

from forecasting.time_series_model import gp
from forecasting.utils import load_holidays, load_timeseries, split_training


class UnivariateScaler:
    """
    Standardizes the data to have mean 0 and unit standard deviation.
    """

    def __init__(self):
        self._mean = None
        self._std = None

    def fit(self, x: list):
        self._mean = np.mean(x)
        self._std = np.std(x)
        return self

    def transform(self, x: list) -> list:
        return (x - self._mean) / self._std

    def fit_transform(self, x: list) -> list:
        self.fit(x)
        return self.transform(x)

    def inverse_transform(self, x: list) -> list:
        return x * self._std + self._mean


class Forecast:
    """
    Initialises, trains and makes predictions for the time series model.

    Attributes
    ----------
    mcmc: Instance of numpyro.infer MCMC class
    """

    def __init__(self, mcmc: MCMC):
        self.timeseries = load_timeseries()
        self.holidays = load_holidays()
        self.mcmc = mcmc
        self.training_hours = None
        self.historic_hours = None
        self.forecast_hours = None

        # These are instantiated at training time
        self.x_scaler = None
        self.L = None
        self.training_start_date = None

    def train(
        self,
        rng_key: jnp.ndarray,
        date: pd.Timestamp,
        training_hours: int,
    ):
        """
        Prepares training data and trains model.

        Parameters
        ----------
        rng_key: jax RNG key
        date: timestamp
            When forecast begins
        training_hours: int
            Number of hours data to be trained on
        """
        self.training_hours = training_hours
        y_train = self.prepare_training_data(date)
        training_data = self.prepare_data_dictionary(y_train, is_training=True)
        self.mcmc.run(rng_key, **training_data)

    def prepare_training_data(self, date: pd.Timestamp) -> pd.Series:
        """Prepares training data."""
        training_ids = split_training(
            self.timeseries.index, date, self.training_hours
        )
        y_train = self.timeseries.iloc[training_ids]
        return y_train

    def forecast_admissions(
        self,
        rng_key: jnp.ndarray,
        date: pd.Timestamp,
        historic_hours: int,
        forecast_hours: int,
    ) -> dict:
        """
        Forecasts the admissions due on a certain date based on the
        trained model.

        Parameters
        ----------
        rng_key: jax RNG key
        date: timestamp
            When forecast begins
        historic_hours: int
            Number of hours in the past for forecast to be returned for
        forecast_hours: int
            Number of hours in the future for forecast to be returned for

        Returns
        -------
        results: dict
            Keys are 'time' and 'posterior' which contain a 1d array of
            timestamps and the posterior for patient numbers respectively
        """
        self.historic_hours = historic_hours
        self.forecast_hours = forecast_hours
        y_forecast = self.prepare_forecast_data(
            date - (pd.Timedelta("1H") * self.historic_hours)
        )
        forecast_data = self.prepare_data_dictionary(
            y_forecast, is_training=False
        )
        prediction = self.predict(rng_key, **forecast_data)
        results = {}
        results["time"] = y_forecast.index
        results["posterior"] = prediction
        return results

    def prepare_forecast_data(self, date: pd.Timestamp) -> pd.Series:
        """Prepares forecast data."""
        forecast_datetimes = pd.date_range(
            date,
            periods=self.historic_hours + self.forecast_hours,
            freq="1H",
        )
        times = (
            pd.DataFrame(data={"time": forecast_datetimes})
            .groupby(by="time")
            .count()
        )
        return times

    def prepare_data_dictionary(
        self, y: pd.Series, is_training: bool = True
    ) -> dict:
        """Puts training or forecast data into dictionary."""
        if is_training:
            # reset the scaler in each training, re-use if validating
            self.x_scaler = UnivariateScaler()
            self.training_start_date = y.index.min()

        x = (y.index - self.training_start_date) / pd.Timedelta("1H")
        xsd = self.x_scaler.fit_transform(x)

        if is_training:
            self.L = 1.5 * max(xsd)

        day_of_week = y.index.day_of_week
        hour_of_day = y.index.hour
        is_holiday = [d.date() in self.holidays.date for d in y.index]

        return {
            "y": jnp.array(y.values) if is_training else None,
            "x": jnp.array(xsd),
            "day_of_week": jnp.array(day_of_week),
            "hour_of_day": jnp.array(hour_of_day),
            "is_holiday": jnp.array(is_holiday),
            "L": self.L,
            "M": 10,
        }

    def predict(self, rng_key: jnp.ndarray, *args, **kwargs) -> dict:
        """Gets predictions from time series mdoel."""
        predictive = Predictive(
            self.mcmc.sampler.model, posterior_samples=self.mcmc.get_samples()
        )
        prediction = predictive(rng_key, *args, **kwargs)
        return prediction["y"]


class PatientForecast:
    """
    Wrapper for Forecast class.
    """

    def __init__(self):
        self.key = self.setup()
        self.model = self.init_model()

    def setup(self) -> jnp.ndarray:
        """Sets number of CPUs and random seed."""

        NUM_CPUS = int(os.environ.get("NUM_CPUS", os.cpu_count()))
        numpyro.set_host_device_count(NUM_CPUS)

        # set a random seed
        rng_key = jax.random.PRNGKey(1)

        return jax.random.split(rng_key, num=1)[0]

    def init_model(self) -> Forecast:
        """Initialises the model."""

        mcmc = MCMC(
            NUTS(gp, init_strategy=init_to_median),
            num_warmup=2000,
            num_samples=2000,
            num_chains=4,
        )

        forecast_model = Forecast(mcmc)

        return forecast_model

    def train_model(self, date: pd.Timestamp, training_hours: int):
        """
        Trains the model based on past data.

        Parameters
        ----------
        date: timestamp
            When forecast begins
        training_hours: int
            Number of hours data to be trained on
        """

        self.model.train(self.key, date, training_hours)

    def call_forecast(
        self, date: pd.Timestamp, historic_hours: int, forecast_hours: int
    ) -> dict:
        """
        Makes predictions for patient numbers on new date.

        Parameters
        ----------
        date: timestamp
            When forecast begins
        historic_hours: int
            Number of hours in the past for forecast to be returned for
        forecast_hours: int
            Number of hours in the future for forecast to be returned for

        Returns
        -------
        results: dict
            Keys are 'time' and 'posterior' which contain a 1d array of
            timestamps and the posterior for patient numbers respectively
        """

        results = self.model.forecast_admissions(
            self.key, date, historic_hours, forecast_hours
        )

        return results

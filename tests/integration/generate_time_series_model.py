# This file was generated from notebooks/4.Time_Series_Forecast.ipynb

# Import required modules
import os
import pickle
import pandas as pd

from forecasting.forecast import PatientForecast
from forecasting.utils import (
    FORECAST_HOURS,  # 24
    HISTORIC_HOURS,  # 168
    HOURS_IN_WEEK,  # 168
    START_FORECAST,  # 01/05/1855 00:00
)

# Initialise class
forecast_model = PatientForecast()

# Train model, with training period ending at START_FORECAST
forecast_model.train_model(START_FORECAST, training_hours=1440)

# Get prediction for 1 week before START_FORECAST and 24hrs after a week after START_FORECAST
results = forecast_model.call_forecast(
    START_FORECAST,
    historic_hours=HISTORIC_HOURS,
    forecast_hours=HOURS_IN_WEEK + FORECAST_HOURS,
)
# Save results

pickle.dump(results, open("../../data/forecast_results.pkl", "wb"))
print("Saved forecast_results.pkl")

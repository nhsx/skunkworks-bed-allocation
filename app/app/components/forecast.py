import json
import os
import pickle

import dash_bootstrap_components as dbc
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output, State

from forecasting.utils import map_to_date, split_historic_forecast

from .. import api
from ..app import app

DIRNAME = os.path.dirname(__file__)

if api.REAL_DATA:

    try:
        AGG_PERCENTILES = pickle.load(
            open(
                os.path.join(
                    DIRNAME, "../data/forecast_aggregated_percentiles.pkl"
                ),
                "rb",
            )
        )
    except FileNotFoundError as e:
        print("Aggregated forecast data not found, see "
            "app/app/data/get_forecast_percentiles.py")
        raise e

try:
    SPLIT = pickle.load(
        open(os.path.join(DIRNAME, "../data/forecast_split_random.pkl"), "rb",)
    )
except FileNotFoundError as e:
    print("Forecast breakdown file not found, see "
        "app/app/data/get_forecast_split.py")
    raise e

# ------------- Components -------------

day_selector = dcc.Dropdown(
    id="day_selection",
    options=[
        {"label": day, "value": day}
        for day in [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
    ],
    value="Monday",
    style={"width": "150px"},
)

time_selector = dcc.Dropdown(
    id="time_selection",
    options=[{"label": f"{i}:00", "value": i} for i in range(24)],
    value=9,
    style={"width": "100px"},
)

generate_forecast_button = dbc.Button(
    "GENERATE FORECAST", id="generate_forecast", style={"width": "260px"},
)

forecast_figure = dcc.Graph(
    id="forecast_figure", style={"height": "100%", "width": "100%"},
)


# ------------- Structure -------------


forecast_block = dbc.Card(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col([generate_forecast_button], width=6,),
                        dbc.Col(
                            dbc.Row(
                                [day_selector, time_selector],
                                justify="end",
                                align="end",
                            ),
                            width=6,
                            align="end",
                        ),
                        dcc.Store(id="forecast_data"),
                    ],
                    className="p-2",
                    justify="end",
                ),
                dbc.Row([forecast_figure,], className="p-2", justify="end",),
                dbc.Row(id="forecast_details"),
            ],
            className="p-4",
        )
    ],
    style={"height": 550},
)


# ------------- Display -------------


def print_forecast_details(forecast_data, day, time):
    """
    Takes forecast, finds the 5th and 95th percentile for admission numbers
    and splits in gender, division, etc.
    """

    # Finds date within forecast window for that day of week and hour of day
    date = map_to_date(day, time)

    # Only need percentiles and splits for the current hour
    historic_hours = 0
    forecast_hours = 1

    if api.REAL_DATA:

        # Cut percentiles to current hour
        historic_ids, forecast_ids = split_historic_forecast(
            AGG_PERCENTILES["time"], date, historic_hours, forecast_hours
        )
        percentile_5 = AGG_PERCENTILES["lower"][forecast_ids]
        percentile_95 = AGG_PERCENTILES["upper"][forecast_ids]

    else:

        # Generate random number for admissions in next 4 hours
        N = 1000
        admissions = np.random.randint(0, high=10, size=(N, 4))
        agg_admissions = [[sum(admissions[i, :]) for i in range(0, N)]]

        # Find 5th and 95th percentiles of N samples
        percentile_5 = np.percentile(agg_admissions, 5)
        percentile_95 = np.percentile(agg_admissions, 95)

    # Cut splits to current hour
    historic_ids, forecast_ids = split_historic_forecast(
        SPLIT["time"], date, historic_hours, forecast_hours
    )
    male = SPLIT["male"][forecast_ids]
    elective = SPLIT["elective"][forecast_ids]
    medical = SPLIT["medical"][forecast_ids]
    over_18 = SPLIT["over_18"][forecast_ids]
    over_65 = SPLIT["over_65"][forecast_ids]

    return dbc.Col(
        [
            dbc.Row(
                html.P(
                    f"In the next 4 hours between {int(percentile_5)}"
                    f" and {int(percentile_95)} admissions are expected."
                ),
            ),
            dbc.Row(html.P("Of these we estimate that: "),),
            dbc.Row(
                html.Ul(
                    [
                        html.Li(
                            f"Sex: {int(male)}% will be male and"
                            f" {int(100-male)}% will be female"
                        ),
                        html.Li(
                            f"Division: {int(medical)}% will be medical and"
                            f" {int(100-medical)}% will be surgical"
                        ),
                        html.Li(
                            f"Age: {int(over_18)}% will be over 18 and"
                            f" {int(over_65)}% will be over 65"
                        ),
                        html.Li(
                            f"Type: {int(elective)}% will be elective and"
                            f" {int(100-elective)}% will be non-elective"
                        ),
                    ]
                ),
            ),
        ]
    )


# ------------- Callbacks -------------


@app.callback(
    Output("forecast_data", "data"),
    [Input("generate_forecast", "n_clicks")],
    [State("day_selection", "value"), State("time_selection", "value")],
)
def get_forecast_data(n_clicks, day, time):
    """
    Gets forecast from model based on time of day and day of week
    """
    forecast_data = api.get_forecast(day, time)
    return json.dumps(forecast_data)


@app.callback(
    Output("forecast_figure", "figure"), [Input("forecast_data", "data")]
)
def populate_forecast_figure(forecast_data_json):
    """
    Creates the plot of the forecast
    """
    forecast_data = json.loads(forecast_data_json)
    fig = api.make_forecast_figure(forecast_data)
    fig.update_layout(hovermode="x unified")
    return api.make_forecast_figure(forecast_data)


@app.callback(
    Output("forecast_details", "children"),
    [Input("forecast_data", "data")],
    [State("day_selection", "value"), State("time_selection", "value")],
)
def forecast_details(forecast_data_json, day, time):
    """
    Updates the text describing the forecast
    """
    forecast_data = json.loads(forecast_data_json)
    return print_forecast_details(forecast_data, day, time)

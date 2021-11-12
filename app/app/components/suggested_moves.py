import json

import cloudpickle
import dash
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State

from .. import api
from ..app import app

# ------------- Components -------------


suggest_moves_button = dbc.Button(
    "SUGGEST ALLOCATIONS",
    id="suggest_moves_button",
    style={"width": "260px"},
)


# ------------- Structure -------------

suggested_moves_block = dbc.Card(
    [
        dbc.Col(
            [
                dbc.Row(
                    dbc.Col(suggest_moves_button, className="p-2 ml-3"),
                ),
                html.Div(
                    "The allocation assistant looks for the best beds"
                    + " available for the current patient. The best beds are"
                    + " those that break the fewest or least important"
                    + " constraints. Use these suggestions alongside the"
                    + " demand forecast to decide where to admit the patient.",
                    style={"padding": 10},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.H5("Suggested beds"),
                            width=6,
                            className="p-0",
                        ),
                        dbc.Col(html.H5("Penalty"), width=3, className="p-0"),
                        dbc.Col(
                            html.H5("Constraints broken"),
                            width=3,
                            className="p-0",
                        ),
                    ],
                    className="m-3",
                ),
                dbc.Row(
                    id="suggested_moves",
                    style={"width": "100%"},
                    className="m-0 p-0",
                ),
                html.Br(),
            ],
            className="p-4",
        )
    ]
)


def make_suggestion_header(i, row):
    return dbc.CardHeader(
        html.H2(
            dbc.Button(
                [print_suggestion_title(row)],
                id=f"suggestion-{i}",
                outline=True,
                style={"text-align": "left", "width": "100%"},
                className="p-0 m-0",
            ),
        ),
        style={"width": "100%"},
    )


def make_suggestion_collapse(i, row):
    return dbc.Collapse(
        dbc.CardBody([print_suggestion_details(row)]),
        id=f"collapse-{i}",
        is_open=False,
    )


def make_suggestion(i, row):
    return dbc.Card(
        [make_suggestion_header(i, row), make_suggestion_collapse(i, row)],
        style={"width": "100%"},
    )


# ------------- Display -------------


def print_suggestion_title(row):
    """
    Creates the visible header of each suggestion.

    Parameters
    ----------
    row: dict
        Row of suggestions dataframe
    """
    return dbc.Row(
        [
            dbc.Col(
                row["Ward Name"],
                width=6,
                className="m-0",
            ),
            dbc.Col(
                row["Penalty Status"],
                width=3,
                style=colour_trafficlight(row["Penalty Status"]),
                className="m-0",
            ),
            dbc.Col(
                row["Number Broken"],
                width=3,
                className="m-0",
            ),
        ],
        className="m-0 p-0",
        justify="left",
        style={"width": "100%"},
    )


def print_suggestion_details(row):
    """
    Creates the contents of each suggestion visible when header is clicked.

    Parameters
    ----------
    row: dict
        Row of suggestions dataframe
    """
    specialty = ", ".join(row["Ward Specialty"]).title()
    return html.Div(
        [
            html.H6("Ward details", style={"color": "#005EB8"}),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Row(f"Bed: {row['Bed']}"),
                            dbc.Row(f"Room Type: {row['Room Type']}"),
                            dbc.Row(
                                " Ward COVID status: "
                                + f"{row['COVID-19 Status']}",
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Row(f"Ward Sex: {row['Ward Sex']}"),
                            dbc.Row(f"Ward Specialty: {specialty}"),
                            dbc.Row(
                                f"Ward Availability: {row['Availability']}"
                            ),
                        ]
                    ),
                ],
                className="ml-3",
            ),
            html.P(),
            html.H6("Broken constraint details", style={"color": "#005EB8"}),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Row(c, style=colour_restrictions(c))
                            for c in row["Clean Restrictions"]
                        ]
                    ),
                ],
                className="ml-3",
            ),
        ]
    )


def colour_trafficlight(input_text):
    if input_text == "High" or input_text == "Red":
        return {"color": "red"}
    elif input_text == "Low" or input_text == "Green":
        return {"color": "green"}
    elif input_text == "Medium" or input_text == "Amber":
        return {"color": "orange"}


def colour_restrictions(input_text):
    if "-" in input_text:
        return {"color": "red"}


# ------------- Callbacks -------------


@app.callback(
    Output("suggested_moves", "children"),
    [Input("suggest_moves_button", "n_clicks")],
    [State("patient_details_data", "data")],
)
def suggest_moves(n_clicks, patient_details):
    """
    Creates suggestions table, where is suggestion is clickable
    Update this function to call both greedy and mcts
    """
    if patient_details is None:
        return None
    patient_details = json.loads(patient_details)

    with open("/tmp/hospital/hospital.pkl", "rb") as f:
        hospital = cloudpickle.load(f)

    # update this call when using the real allocation model
    greedy_suggestions = api.get_greedy_allocations(hospital, patient_details)

    accordion = dbc.Container(
        [
            make_suggestion(i + 1, row)
            for i, row in greedy_suggestions.iterrows()
        ],
        className="accordion",
    )
    return accordion


@app.callback(
    [Output(f"collapse-{i}", "is_open") for i in range(1, 6)],
    [Input(f"suggestion-{i}", "n_clicks") for i in range(1, 6)],
    [State(f"collapse-{i}", "is_open") for i in range(1, 6)],
)
def toggle_accordion_moves(
    n1, n2, n3, n4, n5, is_open1, is_open2, is_open3, is_open4, is_open5
):
    """
    Controls the opening and closing of suggestions on clicks
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, False, False, False, False
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "suggestion-1" and n1:
        return not is_open1, False, False, False, False
    elif button_id == "suggestion-2" and n2:
        return False, not is_open2, False, False, False
    elif button_id == "suggestion-3" and n3:
        return False, False, not is_open3, False, False
    elif button_id == "suggestion-4" and n3:
        return False, False, False, not is_open4, False
    elif button_id == "suggestion-5" and n3:
        return False, False, False, False, not is_open5
    return False, False, False, False, False

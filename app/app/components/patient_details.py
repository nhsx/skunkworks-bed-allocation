import json

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output

from .. import api
from ..app import app

# ------------- Components -------------


generate_patient_button = dbc.Button(
    "NEXT PATIENT",
    id="generate_patient",
    style={"width": "260px"},
)


# ------------- Structure -------------


patient_details_block = dbc.Card(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [generate_patient_button],
                        ),
                        dcc.Store(id="patient_details_data"),
                    ],
                    className="p-2",
                ),
                html.Div(
                    "Press the Next Patient button to generate a new random"
                    + " patient to allocate.",
                    style={"padding": 10},
                ),
                dbc.Row(
                    [
                        dbc.Col(id="patient_details"),
                    ],
                    className="p-2",
                    justify="end",
                ),
            ],
            className="p-4",
        )
    ],
    style={"height": 550},
)


# ------------- Display -------------


def print_patient_details(patient_details):
    """
    Prints the patient details in two columns,
    with number of items in first column set by 'max_items'
    """
    max_items = 7
    return [
        dbc.Col(
            [
                dbc.Row(
                    [dbc.Col(key), dbc.Col(value, style=colour_text(value))]
                )
                for i, (key, value) in enumerate(patient_details.items())
                if i <= max_items
            ]
        ),
        dbc.Col(
            [
                dbc.Row(
                    [dbc.Col(key), dbc.Col(value, style=colour_text(value))]
                )
                for i, (key, value) in enumerate(patient_details.items())
                if i > max_items
            ]
        ),
    ]


def colour_text(input_text):
    if input_text == "Yes" or input_text == "Red":
        return {"color": "red"}
    elif input_text == "Green":
        return {"color": "green"}
    elif input_text == "Amber":
        return {"color": "orange"}


# ------------- Callbacks -------------


@app.callback(
    Output("patient_details_data", "data"),
    [
        Input("generate_patient", "n_clicks"),
    ],
)
def generate_patient_block(n_clicks):
    """
    Generates the patient details and then stores
    """
    patient_details, _ = api.get_patient()
    return json.dumps(patient_details)


@app.callback(
    Output("patient_details", "children"),
    [
        Input("patient_details_data", "data"),
    ],
)
def generate_patient_details_table(patient_details):
    """
    Creates the block containing the patient details
    """
    patient_details = json.loads(patient_details)
    assesment_unit = api.map_assesment_unit(patient_details)
    details_block = dbc.Col(
        [
            dbc.Row(
                html.H5(
                    f"{patient_details.pop('Name')} " f"from {assesment_unit}"
                )
            ),
            dbc.Row(print_patient_details(patient_details)),
        ]
    )
    return details_block

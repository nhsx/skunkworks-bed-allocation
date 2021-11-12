from pathlib import Path

import cloudpickle
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State

from .. import api
from ..app import app

# ------------- Components -------------


generate_hospital_button = dbc.Button(
    "RESET HOSPITAL",
    id="generate_hospital",
    style={"width": "260px"},
)


# ------------- Structure -------------


virtual_hospital_block = dbc.Card(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [generate_hospital_button],
                        ),
                        dcc.Store(id="hospital_update"),
                    ],
                    className="p-2",
                ),
                html.Div(
                    "Press the Reset Hospital button to repopulate the"
                    + " hospital with a new random configuration. The PoC"
                    + " hospital has a reduced set of 14 wards, including 10"
                    + " adult medicine and 4 surgical wards.",
                    style={"padding": 10},
                ),
            ],
            className="p-4",
        ),
        dbc.Spinner(
            dbc.Row(
                id="hospital_block",
                style={"width": "100%"},
                className="m-0 p-0",
            )
        ),
    ],
)


def make_ward_header(ward):
    return dbc.CardHeader(
        html.H2(
            dbc.Button(
                [print_ward_details(ward)],
                id=f"ward-{ward.name}",
                outline=True,
                style={"text-align": "left", "width": "100%"},
                className="p-0 m-0",
            ),
        ),
        style={"width": "100%"},
    )


def make_ward_collapse(ward):
    return dbc.Collapse(
        dbc.CardBody(
            [
                dbc.Col(
                    [
                        dbc.Row(print_room_details(room)),
                        dbc.Row(
                            print_bed_details(room),
                            className="ml-3",
                        ),
                    ]
                )
                for room in ward.rooms
            ]
        ),
        id=f"collapse-ward-{ward.name}",
        is_open=False,
    )


def make_hospital_display(ward):
    return dbc.Card(
        [
            make_ward_header(ward),
            make_ward_collapse(ward),
        ],
        style={"width": "100%"},
    )


# ------------- Display -------------


def print_ward_details(ward):
    """
    Displays the top level details of each ward.
    This display is clickable to reveal details of rooms and beds
    """
    occupancy = api.calc_occupancy(ward)
    return dbc.Row(
        [
            dbc.Col(
                ward.name,
                width=6,
                className="m-0",
            ),
            dbc.Col(
                (
                    f"{occupancy['occupied']} out of  {occupancy['total']} ",
                    "beds occupied",
                ),
                width=3,
                className="m-0",
            ),
        ],
        className="m-0 p-0",
        justify="left",
        style={"width": "100%"},
    )


def print_room_details(room):
    """
    Prints details of the room within the ward
    """
    return dbc.Col(f"{api.get_room_type(room)}: {room.name}")


def print_bed_details(room):
    """
    Prints details of the bed within the room
    """
    return dbc.Col(
        [
            dbc.Row(
                [
                    dbc.Col([html.P(bed.name)], style=colour_bed(bed)),
                    dbc.Col(
                        [
                            html.P(
                                [
                                    html.Span(
                                        bed.patient.name
                                        if bed.patient is not None
                                        else "available",
                                        id=f"tooltip-patient-{bed.name}",
                                        style={
                                            "textDecoration": "underline",
                                            "cursor": "pointer",
                                        },
                                    )
                                ]
                            ),
                            dbc.Tooltip(
                                f"Sex: {bed.patient.sex.name}, "
                                f"Weight: {int(bed.patient.weight)}"
                                if bed.patient is not None
                                else "",
                                target=f"tooltip-patient-{bed.name}",
                            ),
                        ],
                    ),
                ]
            )
            for bed in room.beds
        ]
    )


def colour_bed(bed):
    if not bed.patient:
        return {"color": "green"}


# ------------- Callbacks -------------


@app.callback(
    Output("hospital_block", "children"),
    [Input("hospital_update", "data")],
)
def display_hospital(n_clicks):
    """
    Creates a clickable display of the wards in the hospital
    """
    with open("/tmp/hospital/hospital.pkl", "rb") as f:
        hospital = cloudpickle.load(f)

    hosp_accordion = dbc.Container(
        [make_hospital_display(ward) for ward in hospital.wards],
        className="accordion",
    )
    return hosp_accordion


@app.callback(
    Output("hospital_update", "data"),
    [Input("generate_hospital", "n_clicks")],
)
def get_hospital(n_clicks):
    """
    Creates a populated hospital on button click
    """
    hospital = api.get_populated_hospital(0.95)

    Path("/tmp/hospital").mkdir(parents=True, exist_ok=True)
    with open("/tmp/hospital/hospital.pkl", "wb") as f:
        cloudpickle.dump(hospital, f)
    return {"update": "true"}


@app.callback(
    [
        Output(f"collapse-ward-{ward}", "is_open")
        for ward in api.WARDS["Ward name"]
    ],
    [Input(f"ward-{ward}", "n_clicks") for ward in api.WARDS["Ward name"]],
    [
        State(f"collapse-ward-{ward}", "is_open")
        for ward in api.WARDS["Ward name"]
    ],
)
def toggle_accordion_hospital(
    n1,
    n2,
    n3,
    n4,
    n5,
    n6,
    is_open1,
    is_open2,
    is_open3,
    is_open4,
    is_open5,
    is_open6,
):
    """
    Ugly but pragmatic function for creating accordian with 14 items
    """
    return_list = [False] * 6
    ns = [n1, n2, n3, n4, n5, n6]
    opens = [
        is_open1,
        is_open2,
        is_open3,
        is_open4,
        is_open5,
        is_open6,
    ]
    ctx = dash.callback_context
    if not ctx.triggered:
        return return_list
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    for i, ward_name in enumerate(api.WARDS["Ward name"]):
        if button_id == f"ward-{ward_name}" and ns[i]:
            return_list[i] = not opens[i]
            return return_list
    return return_list

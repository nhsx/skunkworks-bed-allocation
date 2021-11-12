import dash_bootstrap_components as dbc
from dash import html

from .components import (
    forecast_block,
    patient_details_block,
    suggested_moves_block,
    virtual_hospital_block,
)

# To display date in corner of app, uncomment this block and line in title
# from datetime import date
# today = date.today().strftime("%d-%b-%Y")
# date_display = dbc.Col(
#     html.H3(
#         today,
#         style={"text-align": "right"},
#     ),
#     className="pr-3 pt-2",
# )

title = dbc.Card(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H3("KETTERING GENERAL HOSPITAL"),
                    className="pr-3 pt-2",
                ),
                # date_display,
            ],
            justify="between",
            className="p-2",
        ),
    ],
)


content = dbc.Card(
    [
        dbc.Row(title, className="m-0", style={"width": "100%"}),
        dbc.Row(
            [
                dbc.Col(
                    patient_details_block,
                    width=12,
                    xl=6,
                    className="p-0",
                ),
                dbc.Col(
                    forecast_block,
                    width=12,
                    xl=6,
                    className="p-0",
                    style={"height": "100%"},
                ),
            ],
            className="m-0",
        ),
        dbc.Row(
            [
                dbc.Col(
                    virtual_hospital_block, width=12, xl=6, className="p-0"
                ),
                dbc.Col(
                    suggested_moves_block, width=12, xl=6, className="p-0"
                ),
            ],
            className="m-0",
        ),
    ],
)

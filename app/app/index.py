import dash_bootstrap_components as dbc
from dash import html

navbar = dbc.Card(
    [
        dbc.Col(
            [
                dbc.Row(
                    children=[
                        dbc.Col(
                            html.Img(
                                src="/static/images/320px-NHS-Logo.png",
                                height="40px",
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            html.H5("Bed Allocation Tool"),
                            className="text-ibm-plex-sans mt-1",
                            style={
                                "font-size": "36px",
                                "line-height": 45,
                                "color": "#fff",
                            },
                        ),
                    ],
                    align="center",
                    className="p-2",
                ),
            ],
            className="mr",
            width="auto",
        ),
    ],
    className="bg-primary",
)

footer = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Img(
                        src="/static/images/faculty-white-logo.png",
                        height="40px",
                    ),
                    className="m-1",
                    width=2,
                ),
            ]
        )
    ],
    fluid=True,
    className="bg-primary p-2 px-2",
)

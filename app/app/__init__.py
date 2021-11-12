from dash import dcc, html
from dash.dependencies import Input, Output

from .app import app, server
from .index import footer, navbar
from .page import content

__all__ = ["app", "server"]


def serve_layout():
    return html.Div(
        [
            dcc.Location(id="url"),
            html.Div(
                navbar, style={"position": "sticky", "top": 0, "zIndex": 1020}
            ),
            html.Div(content),
            html.Div(footer, style={"bottom": 0, "zIndex": 1020}),
        ],
        style={"min-height": "100vh"},
        className="faculty-bootstrap",
    )


app.layout = serve_layout


def _build_toggler(*ids):
    def toggler(pathname):
        return pathname in [f"/{id_}" for id_ in ids]

    return toggler


for id_ in ["page1"]:
    if id_ == "page1":
        app.callback(Output(id_, "active"), [Input("url", "pathname")])(
            _build_toggler("", id_)
        )
    else:
        app.callback(Output(id_, "active"), [Input("url", "pathname")])(
            _build_toggler(id_)
        )

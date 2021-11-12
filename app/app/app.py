from pathlib import Path

import dash
import flask

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"

STATIC_DIR = Path(__file__).parent / "static"

server = flask.Flask(
    __name__, static_url_path="/static", static_folder=str(STATIC_DIR)
)

app = dash.Dash(
    external_stylesheets=[
        "/static/css/fonts.css",
        "/static/css/core.min.css",
        FONT_AWESOME,
    ],
    server=server,
)

app.title = "Bed Allocation"
app.config.suppress_callback_exceptions = True


# override default html index to add favicon
with open(STATIC_DIR / "html" / "index.html") as f:
    app.index_string = f.read()

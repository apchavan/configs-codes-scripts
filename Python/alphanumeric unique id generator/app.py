import dash
import dash_mantine_components as dmc

import constants
from dash_callbacks import dash_app_instance
from dash_instance import DashInstance

# Below setting is required in Azure AppService deployment.
app = dash_app_instance.server

# Set the initial app layout.
dash_app_instance.layout = dmc.MantineProvider(
    children=[
        dmc.NotificationsProvider(
            position="top-center",
            children=[
                dash.html.Div(
                    children=[
                        dash.html.Div(id="Notifications-View"),
                        dash.dcc.Location(id="App-URL-Location", refresh=False),
                        dash.dcc.Location(id="App-Redirect-Location", refresh=True),
                        dash.html.Div(id="App-Page-Content-View"),
                    ],
                ),
            ],
        )
    ],
)


@dash_app_instance.callback(
    [
        dash.Output("App-Page-Content-View", "children"),
        dash.Output("App-Redirect-Location", "pathname"),
    ],
    dash.Input("App-URL-Location", "pathname"),
)
def set_app_page_content_view(url_str: str):
    """
    Define a callback to determinte the layout & redirecting URL to return.
    """
    view = DashInstance.get_main_layout()
    url_pathname = "/"
    return view, url_pathname


if __name__ == "__main__":
    dash_app_instance.run(
        host=constants.HOST_ADDRESS,
        port=constants.DASH_PORT_NO,
        debug=constants.IS_DASH_DEBUG_MODE,
    )

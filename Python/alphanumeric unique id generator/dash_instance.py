import os
import multiprocessing

import dash
import dash_mantine_components as dmc

import constants
import utility_functions


class DashInstance:
    """
    Class that create & hold the `dash` application instance, layout and other shared objects for easy access.
    """

    # Dash application object.
    _dashAppInstance: dash.Dash = None

    # Multiprocessing lock object to protect from data race conditions.
    _multiprocessing_lock: multiprocessing.Lock = None

    @staticmethod
    def _create_instance() -> None:
        """`Private method.`"""

        # Create application instance.
        DashInstance._dashAppInstance = dash.Dash(
            name=__name__,
            # server=FlaskServerManager.get_server_instance(),
            # assets_folder=os.path.join("..", "assets"),
            title=constants.APP_NAME,
            prevent_initial_callbacks=False,
            suppress_callback_exceptions=True,
            external_stylesheets=[os.path.join("assets", "app_style.css")],
        )

    @staticmethod
    def get_instance() -> dash.Dash:
        """
        Return the application instance ensuring only one instance exist at once.

        `Public method.`
        """
        if DashInstance._dashAppInstance is None:
            DashInstance._create_instance()

        return DashInstance._dashAppInstance

    @staticmethod
    def get_multiprocessing_lock() -> multiprocessing.Lock:
        """
        Return the multiprocessing lock object for avoiding data race conditions.

        `Public method.`
        """
        if DashInstance._multiprocessing_lock is None:
            DashInstance._multiprocessing_lock = multiprocessing.Lock()

        return DashInstance._multiprocessing_lock

    @staticmethod
    def get_main_layout() -> dash.html.Div:
        """
        Returns main layout for `dash` application.

        `Public method.`
        """

        return dash.html.Div(
            children=[
                dmc.Center(
                    children=[
                        dmc.LoadingOverlay(
                            # mih=f"{MAIN_LAYOUT_CARDS_HEIGHT}px",
                            overlayBlur=5,
                            transitionDuration=500,
                            children=dmc.Stack(
                                miw="22vw",
                                maw="22vw",
                                mih="90vh",
                                mah="90vh",
                                align="stretch",
                                justify="center",
                                spacing="xl",
                                children=[
                                    dmc.Stack(
                                        spacing="0",
                                        align="center",
                                        children=[
                                            dmc.Title(
                                                children=constants.APP_NAME.strip(),
                                                order=3,
                                                style={
                                                    "color": constants.TVS_TEXT_RGBA_COLOR,
                                                    "margin": "0 auto",
                                                },
                                            ),
                                            dmc.Text(
                                                color="gray",
                                                size="xs",
                                                transform="none",
                                                children=[
                                                    "Version: ",
                                                    constants.APP_VERSION,
                                                ],
                                            ),
                                        ],
                                    ),
                                    dmc.Select(
                                        id="part-category-select",
                                        label="Part Category",
                                        description=dmc.Text(
                                            "Search and select a part category.",
                                            color="black",
                                        ),
                                        placeholder="",
                                        searchable=True,
                                        nothingFound="Part category not found...",
                                        value="",
                                        data=utility_functions.get_product_categories(),
                                    ),
                                    dmc.MultiSelect(
                                        id="cap-color-code-multiselect",
                                        label="Cap Color Code",
                                        description=dmc.Text(
                                            "Select cap color code(s), related to above part category.",
                                            color="black",
                                        ),
                                        placeholder="",
                                        searchable=True,
                                        nothingFound="Color code not found...",
                                        # value=[],
                                        # data=[],
                                    ),
                                    dmc.TextInput(
                                        id="special-code-textinput",
                                        label="Special Code",
                                        description=dmc.Text(
                                            "Type a special code to use with generation process.",
                                            color="black",
                                        ),
                                        placeholder="Optional, and can be empty.",
                                    ),
                                    dmc.NumberInput(
                                        id="unique-ids-to-generate-numberinput",
                                        label="How Many Unique IDs To Generate?",
                                        description=dmc.Stack(
                                            spacing="0",
                                            align="flex-start",
                                            justify="flex-start",
                                            children=[
                                                dmc.Text(
                                                    f"Max quota: {constants.MAX_UNIQUE_ID_GENERATION_LIMIT} IDs per 24 hours.",
                                                    color="black",
                                                ),
                                                dmc.Highlight(
                                                    id="remaining-quota-highlight",
                                                    children=f"Remaining quota: {utility_functions.get_google_api_remaining_quota()}",
                                                    color="black",
                                                    highlightColor="yellow"
                                                    if (
                                                        utility_functions.get_google_api_remaining_quota()
                                                        > 0
                                                    )
                                                    else "red",
                                                    highlight=f"Remaining quota: {utility_functions.get_google_api_remaining_quota()}",
                                                ),
                                            ],
                                        ),
                                        placeholder="Type a value here.",
                                        stepHoldDelay=500,
                                        stepHoldInterval=100,
                                        value=0,
                                        min=10
                                        if (
                                            10
                                            < utility_functions.get_google_api_remaining_quota()
                                        )
                                        else utility_functions.get_google_api_remaining_quota(),
                                        max=utility_functions.get_google_api_remaining_quota(),
                                    ),
                                    dmc.Space(),
                                    dmc.Button(
                                        id="generate-unique-ids-button",
                                        children="Generate Unique IDs",
                                        variant="filled",
                                        color="green",
                                        size="md",
                                        radius="lg",
                                    ),
                                    dmc.Alert(
                                        children=dmc.Stack(
                                            children=[
                                                dmc.Text(
                                                    "Google API constraints & recommendations:",
                                                    size="sm",
                                                ),
                                                dmc.List(
                                                    size="xs",
                                                    withPadding=False,
                                                    children=[
                                                        dmc.ListItem(
                                                            f"Maximum quota is {constants.MAX_UNIQUE_ID_GENERATION_LIMIT} requests in 24 hours.",
                                                        ),
                                                        dmc.ListItem(
                                                            "This quota gets reset everyday at 01:30 PM (IST)."
                                                        ),
                                                        dmc.ListItem(
                                                            "To avoid quota expiry per second, it's better to \ngenerate 1 large batch of categories per 24 hours."
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        title="Note",
                                        color="violet",
                                        variant="light",
                                        radius="lg",
                                        withCloseButton=False,
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        )

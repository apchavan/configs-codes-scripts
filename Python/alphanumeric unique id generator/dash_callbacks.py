import multiprocessing

import dash
import dash_mantine_components as dmc

import constants
import dash_instance
import utility_functions
import uid_generator


# Get application instance to register callback handlers.
dash_app_instance: dash.Dash = dash_instance.DashInstance.get_instance()

############### Callback Function Definitions ###############


@dash_app_instance.callback(
    [
        dash.Output("cap-color-code-multiselect", "disabled"),
        dash.Output("cap-color-code-multiselect", "data"),
        dash.Output("cap-color-code-multiselect", "value"),
        dash.Output("special-code-textinput", "disabled"),
        dash.Output("special-code-textinput", "value"),
        dash.Output("remaining-quota-highlight", "children"),
        dash.Output("remaining-quota-highlight", "highlight"),
        dash.Output("remaining-quota-highlight", "highlightColor"),
    ],
    dash.Input("part-category-select", "value"),
)
def category_select_callback(part_category_value):
    """
    Callback that handles things when category input gets selected or changed.
    """

    # Remove previous tracking if there're older processes exist which might be older than yesterday.
    with dash_instance.DashInstance.get_multiprocessing_lock() as mp_lock:
        utility_functions.remove_old_id_generation_task_entries()

    # Prepare remaining quota highlighting values.
    remaining_quota_children_str: str = (
        f"Remaining quota: {utility_functions.get_google_api_remaining_quota()}"
    )
    if utility_functions.get_google_api_remaining_quota() <= 0:
        remaining_quota_children_str = f"Remaining quota: Expired, no quota left."

    remaining_quota_highlight_str: str = remaining_quota_children_str
    remaining_quota_highlight_color_str: str = (
        "yellow" if (utility_functions.get_google_api_remaining_quota() > 0) else "red"
    )

    if (
        part_category_value is None
        or not isinstance(part_category_value, str)
        or part_category_value.strip() == ""
    ):
        return (
            True,
            [],
            [],
            True,
            "",
            remaining_quota_children_str,
            remaining_quota_highlight_str,
            remaining_quota_highlight_color_str,
        )

    mapped_color_codes_list: list = utility_functions.get_mapped_color_codes(
        short_category=part_category_value,
    )

    # Get list of all values in color code mapping, so they will be shown as default selected values.
    color_values_list: list = []
    for color_code_dict in mapped_color_codes_list:
        value_str: str = color_code_dict["value"]
        color_values_list.append(value_str)

    return (
        False,
        mapped_color_codes_list,
        color_values_list,
        False,
        "",
        remaining_quota_children_str,
        remaining_quota_highlight_str,
        remaining_quota_highlight_color_str,
    )


@dash_app_instance.callback(
    [
        dash.Output("unique-ids-to-generate-numberinput", "value"),
        dash.Output("unique-ids-to-generate-numberinput", "disabled"),
        dash.Output("unique-ids-to-generate-numberinput", "min"),
        dash.Output("unique-ids-to-generate-numberinput", "max"),
    ],
    dash.Input("cap-color-code-multiselect", "value"),
)
def color_cap_code_multiselect_callback(cap_color_code_values):
    """
    Callback that handles things when color cap input gets selected or changed.
    """
    if cap_color_code_values is None or len(cap_color_code_values) <= 0:
        return (
            0,
            True,
            10
            if (10 < utility_functions.get_google_api_remaining_quota())
            else utility_functions.get_google_api_remaining_quota(),
            utility_functions.get_google_api_remaining_quota(),
        )

    return (
        0,
        False,
        10
        if (10 < utility_functions.get_google_api_remaining_quota())
        else utility_functions.get_google_api_remaining_quota(),
        utility_functions.get_google_api_remaining_quota(),
    )


@dash_app_instance.callback(
    dash.Output("generate-unique-ids-button", "disabled"),
    dash.Input("unique-ids-to-generate-numberinput", "value"),
)
def unique_ids_numberinput_callback(unique_ids_numberinput):
    """
    Callback that handles things when provided input for unique .
    """

    if (
        unique_ids_numberinput is None
        or str(unique_ids_numberinput).strip() == ""
        or int(unique_ids_numberinput) <= 0
        or int(unique_ids_numberinput) > constants.MAX_UNIQUE_ID_GENERATION_LIMIT
    ):
        return True

    return False


@dash_app_instance.callback(
    [
        dash.Output("Notifications-View", "children"),
        dash.Output("part-category-select", "value"),
    ],
    [
        dash.Input("generate-unique-ids-button", "n_clicks"),
        dash.State("part-category-select", "value"),
        dash.State("cap-color-code-multiselect", "value"),
        dash.State("special-code-textinput", "value"),
        dash.State("unique-ids-to-generate-numberinput", "value"),
    ],
)
def generate_unique_ids_callback(
    generate_button_n_clicks,
    part_category_value,
    cap_color_code_values,
    special_code_value,
    unique_ids_numberinput,
):
    if generate_button_n_clicks is None or generate_button_n_clicks <= 0:
        return (
            dash.no_update,
            dash.no_update,
        )

    # Start a separate process to generate all unique IDs.
    # Reference : https://stackoverflow.com/a/2046630

    print(
        f"part_category_value={type(part_category_value)}\ncap_color_code_values={type(cap_color_code_values)}\nspecial_code_value={special_code_value}\nunique_ids_numberinput={type(unique_ids_numberinput)}"
    )

    process: multiprocessing.Process = multiprocessing.Process(
        target=uid_generator.generate_unique_ids,
        args=(
            part_category_value,
            cap_color_code_values,
            str(special_code_value).strip().upper(),
            unique_ids_numberinput,
        ),
    )
    process.start()

    notification_title = "Started unique ID generation process!"
    notification_message = f"File with total {unique_ids_numberinput} unique IDs will be sent on e-mail.\nYou can close this tab now."
    notification_children = dmc.Notification(
        title=dmc.Text(
            children=notification_title,
            transform="capitalize",
            weight=500,
        ),
        id="Upload-And-Indexing-Success-Notification",
        action="show",
        autoClose=False,
        disallowClose=False,
        loading=True,
        color="",
        message=notification_message,
    )

    return (
        notification_children,
        "",
    )

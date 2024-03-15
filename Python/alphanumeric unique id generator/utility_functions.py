import datetime
import pytz
import os

import numpy as np
import pandas as pd

import constants


def _get_category_colors_file_path() -> str:
    """
    Returns the CSV file path where category and colors are stored.
    """
    os.makedirs(name=constants.INTERNAL_DATA_DIRPATH, exist_ok=True)

    category_colors_file_path: str = os.path.join(
        constants.INTERNAL_DATA_DIRPATH,
        "category_colors.csv",
    )

    if not os.path.exists(category_colors_file_path):
        return ""
    return category_colors_file_path


def get_product_categories() -> list:
    """
    Returns the `list` containing `dict`s of unique product categories.

    The returned list will be of following form:

    [
        {"value": "BE", "label": "BE - Beta"},
        {"value": "AL", "label": "AL - Alpha"},
        {"value": "GA", "label": "GA - Gamma"},
    ]
    """
    category_colors_file_path: str = _get_category_colors_file_path()

    categories_df: pd.DataFrame = pd.read_csv(category_colors_file_path)

    unique_short_categories_list: list = (
        categories_df["SHORT_CATEGORY"].unique().tolist()
    )
    result_categories_list: list = []

    for short_category in unique_short_categories_list:
        actual_category: str = categories_df.loc[
            categories_df["SHORT_CATEGORY"] == short_category, "ACTUAL_CATEGORY"
        ].iat[0]
        data_dict: dict = {
            "value": short_category,
            "label": short_category + " - " + actual_category,
        }
        result_categories_list.append(data_dict)

    return result_categories_list


def get_mapped_color_codes(short_category: str) -> list:
    """
    Returns the `list` containing `dict`s of mapped color codes belonging to `short_category`.

    The returned list will be of following form:

    [
        {"value": "BLK", "label": "BLK (Black)"},
        {"value": "RED", "label": "RED (Red)"},
        {"value": "BLU", "label": "BLU (Blue)"},
    ]
    """
    category_colors_file_path: str = _get_category_colors_file_path()

    categories_df: pd.DataFrame = pd.read_csv(category_colors_file_path)

    result_categories_list: list = []

    short_color_codes_list: list = (
        categories_df.loc[
            categories_df["SHORT_CATEGORY"] == short_category, "SHORT_COLOR"
        ]
        .unique()
        .tolist()
    )

    for short_color in short_color_codes_list:
        actual_color: str = categories_df.loc[
            (categories_df["SHORT_CATEGORY"] == short_category)
            & (categories_df["SHORT_COLOR"] == short_color),
            "ACTUAL_COLOR",
        ].iat[0]
        data_dict: dict = {
            "value": short_color,
            "label": short_color + " (" + actual_color + ")",
        }
        result_categories_list.append(data_dict)

    return result_categories_list


def get_current_datetime_for_IST() -> datetime.datetime:
    """
    Returns current datetime as per IST timezone.
    """
    IST: pytz.tzinfo.DstTzInfo = pytz.timezone("Asia/Kolkata")
    datetime_ist: datetime.datetime = datetime.datetime.now(tz=IST)
    return datetime_ist


def get_google_api_remaining_quota() -> int:
    """
    Returns the value of remaining quota for Google's API.
    """
    id_generation_tracking_csv_filepath: str = os.path.join(
        constants.INTERNAL_DATA_DIRPATH,
        constants.ID_GENERATION_TRACKING_CSV_FILENAME,
    )

    if not os.path.exists(id_generation_tracking_csv_filepath):
        return constants.MAX_UNIQUE_ID_GENERATION_LIMIT

    # Calculate consumed quota.
    id_tracking_df: pd.DataFrame = pd.read_csv(
        id_generation_tracking_csv_filepath,
    )
    consumed_quota: int = id_tracking_df["TOTAL_IDS_TO_GENERATE"].sum()

    # Return remaining quota.
    remaining_quota: int = constants.MAX_UNIQUE_ID_GENERATION_LIMIT - consumed_quota

    return remaining_quota if (remaining_quota >= 0) else 0


def write_id_generation_task_entry(
    part_category: str,
    special_code: str,
    max_generate_limit: int,
) -> None:
    """
    Used to write tracking details before some ID generation process being started.
    """
    if (
        part_category is None
        or not isinstance(part_category, str)
        or part_category.strip() == ""
        or special_code is None
        or not isinstance(special_code, str)
        or max_generate_limit is None
        or not isinstance(max_generate_limit, int)
        or max_generate_limit <= 0
    ):
        # Return early if any of this function parameter is not valid.
        return

    id_generation_tracking_csv_filepath: str = os.path.join(
        constants.INTERNAL_DATA_DIRPATH,
        constants.ID_GENERATION_TRACKING_CSV_FILENAME,
    )

    # Based on whether file exist or not, set the proper header status.
    header_state: bool = False
    if not os.path.isfile(id_generation_tracking_csv_filepath):
        header_state = True

    # Create necessary DataFrame and write to CSV file in 'Append' mode.
    # Reason for passing values as list: https://stackoverflow.com/a/17840195
    id_tracking_df: pd.DataFrame = pd.DataFrame(
        data={
            "PART_CATEGORY": [part_category.strip()],
            "SPECIAL_CODE": [special_code.strip()],
            "TOTAL_IDS_TO_GENERATE": [max_generate_limit],
            "GENERATION_START_DATETIME": [
                get_current_datetime_for_IST().strftime(
                    constants.ID_GENERATION_TRACKING_DATETIME_FORMAT
                )
            ],
        },
    )
    id_tracking_df.to_csv(
        id_generation_tracking_csv_filepath,
        mode="a",
        index=False,
        header=header_state,
    )


def remove_old_id_generation_task_entries() -> None:
    """
    Remove previous tracking if there're older processes exist which might be older than yesterday.
    """
    id_generation_tracking_csv_filepath: str = os.path.join(
        constants.INTERNAL_DATA_DIRPATH,
        constants.ID_GENERATION_TRACKING_CSV_FILENAME,
    )

    if not os.path.isfile(id_generation_tracking_csv_filepath):
        return

    # Read existing tracking records.
    id_tracking_df: pd.DataFrame = pd.read_csv(
        id_generation_tracking_csv_filepath,
    )
    # Add timezone information for existing datetime column data.
    id_tracking_df["CONVERTED_DATETIME"] = pd.to_datetime(
        id_tracking_df["GENERATION_START_DATETIME"],
        format=constants.ID_GENERATION_TRACKING_DATETIME_FORMAT,
        dayfirst=True,
    ).dt.tz_localize("Asia/Kolkata")

    # Convert timezone enabled column datatype as Python's native datetime column.
    id_tracking_df["CONVERTED_DATETIME"] = np.array(
        id_tracking_df["CONVERTED_DATETIME"].dt.to_pydatetime()
    )

    # Filter out rows which are older than yesterday's 01:00 PM.
    yesterday_datetime: datetime.datetime = datetime.datetime(
        year=datetime.date.today().year,
        month=datetime.date.today().month,
        day=datetime.date.today().day,
        hour=13,
        tzinfo=pytz.timezone("Asia/Kolkata"),
    ) - datetime.timedelta(days=1.0)

    filtered_df: pd.DataFrame = id_tracking_df[
        id_tracking_df["CONVERTED_DATETIME"] >= yesterday_datetime
    ]

    # If data exist after filtering, then overwrite it as a new file, otherwise remove the file.
    if len(filtered_df.index) > 0:
        filtered_df.to_csv(
            id_generation_tracking_csv_filepath,
            columns=[
                "PART_CATEGORY",
                "SPECIAL_CODE",
                "TOTAL_IDS_TO_GENERATE",
                "GENERATION_START_DATETIME",
            ],
            mode="w",
            index=False,
            header=True,
        )
    else:
        os.remove(id_generation_tracking_csv_filepath)


def read_last_alpha_numeric_digit_length(
    part_category: str,
    cap_color: str,
) -> int:
    """
    Read and return existing alpha-numeric digits length in unique ID
    related to `part_category` and `cap_color`.
    """
    os.makedirs(name=constants.ALPHA_NUM_DIGIT_LEN_DIR_PATH, exist_ok=True)

    alpha_num_digit_len_file_path: str = os.path.join(
        constants.ALPHA_NUM_DIGIT_LEN_DIR_PATH,
        f"{part_category.upper()}_{cap_color.upper()}.txt",
    )

    # If related file not exist, then write default one in file and
    # return `DEFAULT_ALPHA_NUM_UNIQUE_ID_LENGTH` as default unique ID length.
    if not os.path.isfile(alpha_num_digit_len_file_path):
        write_new_alpha_numeric_digit_length(
            part_category=part_category,
            cap_color=cap_color,
            value=constants.DEFAULT_ALPHA_NUM_UNIQUE_ID_LENGTH,
        )
        return constants.DEFAULT_ALPHA_NUM_UNIQUE_ID_LENGTH

    with open(alpha_num_digit_len_file_path, mode="r") as file_ptr:
        value: int = int(file_ptr.read())

    return value


def write_new_alpha_numeric_digit_length(
    part_category: str,
    cap_color: str,
    value: int,
) -> None:
    """
    Write new `value` for alpha-numeric digits length in unique ID
    related to `part_category` and `cap_color`.
    """
    os.makedirs(name=constants.ALPHA_NUM_DIGIT_LEN_DIR_PATH, exist_ok=True)

    alpha_num_digit_len_file_path: str = os.path.join(
        constants.ALPHA_NUM_DIGIT_LEN_DIR_PATH,
        f"{part_category.upper()}_{cap_color.upper()}.txt",
    )

    with open(alpha_num_digit_len_file_path, mode="w") as file_ptr:
        file_ptr.write(str(value))


# Handle execution in case launched as a stand-alone script (for debugging/testing only).
if __name__ == "__main__":
    pass
    # print(get_product_categories())
    # print(get_mapped_color_codes(short_category="SY"))

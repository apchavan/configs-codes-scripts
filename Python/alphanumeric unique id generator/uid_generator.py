"""
Script that generate and store the Unique IDs based on part category (2 characters), cap color code (3 characters) and unique alpha-numeric sequence (6 characters).

Example Unique ID representation:
    |AL|            |RED|             |00001A|
    ^^^^            ^^^^^             ^^^^^^^^
    Product Code    Cap Color Code    Alpha-numeric sequence

When combined, it'll result as: "ALRED00001A".

"""

import datetime
import glob
import os
import typing
import time

import pandas as pd

import constants
import encryptor_encoder
import firebase_url_shortner
import utility_functions

from dash_instance import DashInstance


# FILE_FORMATTED_DATETIME_STR: str = f"%d-%m-%Y_%I-%M-%S-%p"
FILE_FORMATTED_DATETIME_STR: str = f"%d-%m-%Y_%I-%M-%p"
COLUMN_FORMATTED_DATE_STR: str = f"%d/%m/%Y"


def _store_unique_id_to_track(
    part_category: str,
    cap_color_code: str,
    special_code: str,
    unique_ids_list: list,
    encrypted_encoded_ids_list: list,
) -> None:
    """
    Stores the next Unique ID in JSON file mapped under specific part category and cap color code.
    """

    # Create a sub-directory to store files of all Unique IDs.
    sub_dir_name: str = constants.TRACKING_INDEXING_DIRPATH  # "Track_Unique_IDs"
    os.makedirs(name=sub_dir_name, exist_ok=True)

    current_datetime: datetime.datetime = (
        utility_functions.get_current_datetime_for_IST()
    )
    file_formatted_datetime_str: str = current_datetime.strftime(
        FILE_FORMATTED_DATETIME_STR
    )

    file_path: str = os.path.join(
        sub_dir_name,
        f"{part_category}_{cap_color_code}_{file_formatted_datetime_str}.csv",
    )

    # Get a count of total Unique IDs.
    total_ids_count: int = len(unique_ids_list)

    # Store Part_Category, Cap_Color_Code, Special_Code, Unique_ID, Encrypted_Encoded_ID, Generated_Date, Is_Scanned, Scanned_Date, Is_Activated, Latitude, Longitude as CSV file.
    result_df: pd.DataFrame = pd.DataFrame(
        data={
            "PART_CATEGORY": [part_category] * total_ids_count,
            "CAP_COLOR_CODE": [cap_color_code] * total_ids_count,
            "SPECIAL_CODE": [special_code] * total_ids_count,
            "UNIQUE_ID": unique_ids_list,
            "ENCRYPTED_ENCODED_ID": encrypted_encoded_ids_list,
            "GENERATED_DATE": [str(datetime.date.today())] * total_ids_count,
            "IS_SCANNED": [False] * total_ids_count,
            "SCANNED_DATE": [None] * total_ids_count,
            "IS_ACTIVATED": [True] * total_ids_count,
            "LATITUDE": [0.0] * total_ids_count,
            "LONGITUDE": [0.0] * total_ids_count,
        },
    )
    result_df.to_csv(file_path, index=False)


def _read_starting_unique_id_from_track(
    part_category: str,
    cap_color_code: str,
    alpha_numeric_digit_length: int,
) -> str:
    """
    Reads the stored Unique ID related to `part_category` and `cap_color_code`.
    """
    # Create a sub-directory where all files of Unique IDs are stored.
    sub_dir_name: str = constants.TRACKING_INDEXING_DIRPATH  # "Track_Unique_IDs"
    os.makedirs(name=sub_dir_name, exist_ok=True)

    # Get file path for latest file stored belonging to current part category and cap color code.
    # Implementation Reference: https://stackoverflow.com/a/168424
    csv_files_path: list = list(
        filter(
            os.path.isfile,
            glob.glob(
                os.path.join(sub_dir_name, f"{part_category}_{cap_color_code}_*.csv")
            ),
        )
    )
    csv_files_path.sort(key=lambda x: os.path.getmtime(x), reverse=False)

    # If file not found, the return zero values as a starting point.
    # TODO: Also check whether CSV file itself is empty.
    if len(csv_files_path) <= 0 or not os.path.exists(csv_files_path[-1]):
        return "0" * alpha_numeric_digit_length

    # Create file name to read the next Unique ID using latest file stored
    # for this part category and cap color code.
    file_path: str = csv_files_path[-1]

    result_df: pd.DataFrame = pd.read_csv(file_path)

    if len(result_df.index) <= 0 or "UNIQUE_ID" not in result_df.columns:
        return "0" * alpha_numeric_digit_length

    # Extract last row from `result_df` as DataFrame.
    last_row_df: pd.DataFrame = result_df.iloc[[-1]].copy(deep=True)

    # Extract current last Unique ID to convert it to next Unique ID.
    next_unique_id_chars: typing.List[str] = list(last_row_df["UNIQUE_ID"].iat[0])

    # Use a boolean to check whether full alpha-numeric digits limit is crossed.
    is_limit_crossed: bool = False

    # Create the next Unique ID based on `next_unique_id_chars`.
    # Increment from last characters ASCII values.
    for prev_idx in range(len(next_unique_id_chars) - 1, -1, -1):
        # Get previous character's ASCII value.
        prev_ascii: int = ord(next_unique_id_chars[prev_idx])

        # Use a boolean to check and avoid multi-incrementing while processing character "A".
        is_set_first_alphabet: bool = False

        # If between 0 to 9.
        if prev_ascii >= 48 and prev_ascii < 58:
            prev_ascii += 1

            # If passed the digit limits, then set to ASCII of 'A'.
            if prev_ascii == 58:
                prev_ascii = ord("A")
                is_set_first_alphabet = (
                    True  # Setting this will tell to avoid incrementing again.
                )

        # If between A to Z.
        if prev_ascii >= 65 and prev_ascii < 91:
            if not is_set_first_alphabet:
                prev_ascii += 1

            if prev_ascii == 91:
                # If passed the alphabet limits (A-Z), then set to '0' and continue with previous character.
                next_unique_id_chars[prev_idx] = "0"

                # If it's first (0-th) index having '0' character,
                # and all other characters are also '0' it means the limit is crossed;
                # then increment length of alpha-numeric digits and break from loop.
                if prev_idx == 0 and "".join(next_unique_id_chars) == "0" * len(
                    next_unique_id_chars
                ):
                    with DashInstance.get_multiprocessing_lock() as mp_lock:
                        utility_functions.write_new_alpha_numeric_digit_length(
                            part_category=part_category,
                            cap_color=cap_color_code,
                            value=len(next_unique_id_chars) + 1,
                        )
                    is_limit_crossed = True
                else:
                    continue

        # If the limit is crossed, then insert character '1' at 0-th place of `unique_id_chars`.
        if is_limit_crossed:
            next_unique_id_chars.insert(0, "1")
        else:
            # Set to character representation of `prev_ascii` and break from the loop since no need to check and increment more characters.
            next_unique_id_chars[prev_idx] = chr(prev_ascii)
        break

    # Read the value for what was stored for "Next_ID".
    starting_id: str = "".join(next_unique_id_chars)
    return (
        starting_id if (starting_id.strip() != "") else "0" * alpha_numeric_digit_length
    )


def _find_and_fix_missing_short_urls(
    input_df: pd.DataFrame,
) -> dict:
    """
    Tries to find if there's any missing short URLs present. If yes, then it tries to fill those untill there's no missing short URLs left. Finally returns a `dict` with all short URLs mapped with their encrypted encoded IDs.
    """

    # Make a copy of input DataFrame to avoid inplace modifications.
    existing_df: pd.DataFrame = input_df.copy(deep=True)

    # Get DataFrame rows where short URL is missing.
    # If the value is missing then it will contain `NaN` values, so fill those with empty string first.
    existing_df.fillna(value="", inplace=True)
    existing_df = existing_df.loc[existing_df["Short Links"] == ""]

    # Extract list of encrypted and encoded IDs to process and fetch their short URLs.
    encrypted_encoded_ids_list: list = existing_df["Encrypted Encoded"].to_list()

    unique_ids_to_short_url_dict: dict = {}

    # Iterate untill all short URLs are fetched.
    while len(encrypted_encoded_ids_list) > 0:
        print(f"\n -- Found {len(encrypted_encoded_ids_list)} missing short URLs...")

        firebase_url_shortner.collect_firebase_short_urls(
            encrypted_encoded_coupon_codes_list=encrypted_encoded_ids_list,
            unique_ids_to_short_url_dict=unique_ids_to_short_url_dict,
        )
        print("Fetched missing, now filling those URLs...")

        # Fill the existing DataFrame where short URLs were missing.
        for encrypted_encoded_key, short_url in unique_ids_to_short_url_dict.items():
            existing_df.loc[
                existing_df["Encrypted Encoded"] == encrypted_encoded_key, "Short Links"
            ] = short_url

        # Try to check if still there's any missing short URL found.
        existing_df.fillna(value="", inplace=True)
        existing_df = existing_df.loc[existing_df["Short Links"] == ""]
        encrypted_encoded_ids_list = existing_df["Encrypted Encoded"].to_list()

    return unique_ids_to_short_url_dict


def _create_csv_record_and_excel_result(
    part_category: str,
    cap_color_code: str,
    special_code: str,
    unique_ids_list: list,
    full_unique_ids_list: list,
    encrypted_encoded_ids_list: list,
    short_links_list: list,
) -> None:
    """
    Create Pandas DataFrame and stores in Excel file.
    """
    ## 1. Create CSV file to record all Unique IDs, which will be used to append to Elasticsearch index.
    _store_unique_id_to_track(
        part_category=part_category,
        cap_color_code=cap_color_code,
        special_code=special_code,
        unique_ids_list=unique_ids_list,
        encrypted_encoded_ids_list=encrypted_encoded_ids_list,
    )

    ## 2. Create Excel file to store user downloadable file.
    # Create a sub-directory where all result Excel files will be stored.
    sub_dir_name: str = constants.RESULT_EXCEL_DIRPATH  # "Result"
    os.makedirs(name=sub_dir_name, exist_ok=True)

    # Get current datetime to create the required file format.
    current_datetime: datetime.datetime = (
        utility_functions.get_current_datetime_for_IST()
    )
    file_formatted_datetime_str: str = current_datetime.strftime(
        FILE_FORMATTED_DATETIME_STR
    )

    file_path: str = os.path.join(
        sub_dir_name,
        f"{part_category}_{cap_color_code}_{file_formatted_datetime_str}.xlsx",
    )

    # Create a mapping for part category and cap color codes, from short forms to full names.
    part_category_short_to_full_dict: dict = {
        "AL": "Alpha",
        "BE": "Beta",
        "GA": "Gamma",
    }
    cap_color_code_short_to_full_dict: dict = {
        "RED": "Red",
        "BLK": "Black",
        "BLU": "Blue",
    }

    # Get a count of total Unique IDs.
    total_ids_count: int = len(full_unique_ids_list)

    result_df: pd.DataFrame = pd.DataFrame(
        data={
            "Product category": [
                part_category_short_to_full_dict[part_category.upper()]
            ]
            * total_ids_count,
            "Cap colour": [cap_color_code_short_to_full_dict[cap_color_code.upper()]]
            * total_ids_count,
            "Unique record": short_links_list,
            "Date of generation": [current_datetime.strftime(COLUMN_FORMATTED_DATE_STR)]
            * total_ids_count,
            # Below columns won't be written but still useful for processing internally.
            "Unique ID": full_unique_ids_list,
            "Encrypted Encoded": encrypted_encoded_ids_list,
            "Short Links": short_links_list,
        },
    )

    # Try to fix all the missing short URLs if have any.
    unique_ids_to_short_url_dict: dict = _find_and_fix_missing_short_urls(
        input_df=result_df,
    )

    # Fill the final DataFrame where short URLs were missing.
    for encrypted_encoded_key, short_url in unique_ids_to_short_url_dict.items():
        result_df.loc[
            result_df["Encrypted Encoded"] == encrypted_encoded_key, "Unique record"
        ] = short_url

    result_df.to_excel(
        file_path,
        sheet_name=f"{part_category}_{cap_color_code}",
        index=False,
        columns=[
            "Product category",
            "Cap colour",
            "Unique record",
            "Date of generation",
        ],
    )


def generate_unique_ids(
    part_category: str,
    cap_color_codes: list,
    special_code: str,
    max_generate_limit: int,
    # alpha_numeric_digit_length: int = None,
    is_debug_mode: bool = False,
) -> None:
    """
    Generates the Unique IDs when provided `part_category` and `cap_color_codes`.

    Args:

    `part_category` - The part category string which is the first prefix for Unique ID.
    `cap_color_codes` - The list of cap color codes which will be the second prefix for Unique ID.
    `special_code` - The special code used to indicate generated Unique IDs for some festival-like purpose.
    `max_generate_limit` - The maximum number of Unique IDs to be generated.
    `alpha_numeric_digit_length` - The digit length for alpha-numeric characters. This will be used to fill left un-used positions with zeros.
    `is_debug_mode` - To check whether the code is running in debug mode. Default is `False`.
    """

    # Remove previous tracking if there're older processes exist which might be older than yesterday.
    with DashInstance.get_multiprocessing_lock() as mp_lock:
        utility_functions.remove_old_id_generation_task_entries()

    # Create entry to track this ID generation process.
    with DashInstance.get_multiprocessing_lock() as mp_lock:
        utility_functions.write_id_generation_task_entry(
            part_category=part_category,
            special_code=special_code,
            max_generate_limit=max_generate_limit,
        )

    duplicates_set: set = set()

    for cap_color in cap_color_codes:
        # Read existing length for alpha-numeric digits.
        alpha_numeric_digit_length: int = 0
        with DashInstance.get_multiprocessing_lock() as mp_lock:
            alpha_numeric_digit_length = (
                utility_functions.read_last_alpha_numeric_digit_length(
                    part_category=part_category,
                    cap_color=cap_color,
                )
            )

        # First check and read from file if there can be a starting ID for current `part_category` and `cap_color`.
        current_starting_unique_id: str = _read_starting_unique_id_from_track(
            part_category=part_category,
            cap_color_code=cap_color,
            alpha_numeric_digit_length=alpha_numeric_digit_length,
        )

        # After getting `current_starting_unique_id`,
        # read length for alpha-numeric digits again to ensure having correct value
        # just in case if getting that ID might increment the length due to crossing limit.
        with DashInstance.get_multiprocessing_lock() as mp_lock:
            alpha_numeric_digit_length = (
                utility_functions.read_last_alpha_numeric_digit_length(
                    part_category=part_category,
                    cap_color=cap_color,
                )
            )

        ## Debug Start
        if is_debug_mode:
            print(f"\n- Starting ID : {current_starting_unique_id}")
            _ = input("Press enter/return key to continue...")
        ## Debug End

        # Get ASCII value for last character.
        last_char_ascii: int = ord(current_starting_unique_id[-1])

        # Get list of characters excluding the part category, cap color code and special code from Unique ID before starting.
        unique_id_chars: typing.List[str] = list(current_starting_unique_id)

        # To store only alpha-numeric values of unique IDs. For e.g., "00001A"
        unique_ids_list: typing.List[str] = []

        # To store entire strings of generated alpha-numeric unique IDs. For e.g., "PRBLK00001A"
        full_unique_ids_list: typing.List[str] = []

        # To store encrypted, encoded form of above `full_unique_ids_list`.
        encrypted_encoded_ids_list: typing.List[str] = []

        # To store short links for above `encrypted_encoded_ids_list`.
        short_links_list: typing.List[str] = []

        start_time: float = time.perf_counter()

        for idx, _ in enumerate(range(max_generate_limit)):
            # Create Unique ID.
            generated_uid: str = (
                part_category
                + cap_color
                + special_code
                + "".join(unique_id_chars).rjust(alpha_numeric_digit_length, "0")
            )

            # Get encrypted and encoded representation of Unique ID.
            encrypted_encoded_id: str = encryptor_encoder.encrypt_encode_unique_id(
                unique_id_str=generated_uid
            )

            # Append results to respective final lists.
            unique_ids_list.append(
                "".join(unique_id_chars).rjust(alpha_numeric_digit_length, "0")
            )
            full_unique_ids_list.append(generated_uid)
            encrypted_encoded_ids_list.append(encrypted_encoded_id)

            ## Debug Start
            if is_debug_mode:
                print("%9d. %s" % ((idx + 1), generated_uid))
                if generated_uid in duplicates_set:
                    print(f"\n Found duplicate : {generated_uid}")
                    _ = input("Press enter/return key to continue...")
            ## Debug End
            duplicates_set.add(generated_uid)

            # If between 0 to 9.
            if last_char_ascii >= 48 and last_char_ascii < 58:
                last_char_ascii += 1

                # If passed the digit limits, then set to ASCII of 'A'.
                if last_char_ascii == 58:
                    last_char_ascii = ord("A")

                # Update last character.
                last_idx: int = len(unique_id_chars) - 1
                unique_id_chars[last_idx] = chr(last_char_ascii)
                continue

            # If between A to Z.
            if last_char_ascii >= 65 and last_char_ascii < 91:
                last_char_ascii += 1

                # If passed the alphabet limits, then set to ASCII of '0'.
                if last_char_ascii == 91:
                    last_char_ascii = ord("0")

                    # Use a boolean to check whether full alpha-numeric digits limit is crossed.
                    is_limit_crossed: bool = False

                    # Increment previous characters ASCII values.
                    # This will exclude the last character and will only consider from first till second last.
                    for prev_idx in range(len(unique_id_chars) - 2, -1, -1):
                        # Get previous character's ASCII value.
                        prev_ascii: int = ord(unique_id_chars[prev_idx])

                        # Use a boolean to check and avoid multi-incrementing while processing character "A".
                        is_set_first_alphabet: bool = False

                        # If between 0 to 9.
                        if prev_ascii >= 48 and prev_ascii < 58:
                            prev_ascii += 1

                            # If passed the digit limits, then set to ASCII of 'A'.
                            if prev_ascii == 58:
                                prev_ascii = ord("A")
                                is_set_first_alphabet = True  # Setting this will tell to avoid incrementing again.

                        # If between A to Z.
                        if prev_ascii >= 65 and prev_ascii < 91:
                            if not is_set_first_alphabet:
                                prev_ascii += 1

                            if prev_ascii == 91:
                                # If passed the alphabet limits (A-Z), then set to '0' and continue with previous character.
                                unique_id_chars[prev_idx] = "0"

                                # If it's first (0-th) index having '0' character,
                                # and all other characters (except last one) are also '0' it means the limit is crossed;
                                # then increment length of alpha-numeric digits and break from loop.
                                if prev_idx == 0 and "".join(
                                    unique_id_chars[:-1]
                                ) == "0" * (alpha_numeric_digit_length - 1):
                                    with DashInstance.get_multiprocessing_lock() as mp_lock:
                                        alpha_numeric_digit_length += 1
                                        utility_functions.write_new_alpha_numeric_digit_length(
                                            part_category=part_category,
                                            cap_color=cap_color,
                                            value=alpha_numeric_digit_length,
                                        )
                                    is_limit_crossed = True
                                    break
                                else:
                                    continue

                        # Set to character representation of `prev_ascii` and break from the loop since no need to check and increment more characters.
                        unique_id_chars[prev_idx] = chr(prev_ascii)
                        break

                    # If the limit is crossed, then insert character '1' at 0-th place of `unique_id_chars`.
                    if is_limit_crossed:
                        unique_id_chars.insert(0, "1")

                # Update last character.
                last_idx: int = len(unique_id_chars) - 1
                unique_id_chars[last_idx] = chr(last_char_ascii)
                continue

        end_time: float = time.perf_counter()
        print(f"Unique ID generation time: {end_time - start_time:.2f} seconds")

        # Call the asynchronous method here to get short URLs for all encrypted, encoded Unique IDs.
        start_time: float = time.perf_counter()
        unique_ids_to_short_url_dict: dict = {}

        firebase_url_shortner.collect_firebase_short_urls(
            encrypted_encoded_coupon_codes_list=encrypted_encoded_ids_list,
            unique_ids_to_short_url_dict=unique_ids_to_short_url_dict,
        )

        end_time: float = time.perf_counter()
        print(f"Short URL generation time: {end_time - start_time:.2f} seconds")

        # For all `encrypted_encoded_ids_list`, extract and store the related short link.
        for encrypted_encoded_id in encrypted_encoded_ids_list:
            short_links_list.append(unique_ids_to_short_url_dict[encrypted_encoded_id])

        # Create and store DataFrame as Excel file for Unique IDs of each color code and part categories having 2 columns.
        # Firstly for actual Unique ID and second for encrypted, encoded variant of that Unique ID.
        _create_csv_record_and_excel_result(
            part_category=part_category,
            cap_color_code=cap_color,
            special_code=special_code,
            unique_ids_list=unique_ids_list,
            full_unique_ids_list=full_unique_ids_list,
            encrypted_encoded_ids_list=encrypted_encoded_ids_list,
            short_links_list=short_links_list,
        )

    # Remove previous tracking if there're older processes exist which might be older than yesterday.
    with DashInstance.get_multiprocessing_lock() as mp_lock:
        utility_functions.remove_old_id_generation_task_entries()


# Handle execution in case launched as a stand-alone script.
if __name__ == "__main__":
    pass
    # 1. For BE-BLK
    # start_time: float = time.perf_counter()
    # generate_unique_ids(
    #     part_category="BE",
    #     cap_color_codes=["BLK"],
    #     special_code="",
    #     max_generate_limit=100,
    #     is_debug_mode=True,
    # )
    # end_time: float = time.perf_counter()
    # print(f"Total processing time for BE-BLK: {end_time - start_time:.2f} seconds")

    # 2. For AL-RED
    # start_time: float = time.perf_counter()
    # generate_unique_ids(
    #     part_category="AL",
    #     cap_color_codes=["RED"],
    #     special_code="",
    #     max_generate_limit=100,
    #     is_debug_mode=True,
    # )
    # end_time: float = time.perf_counter()
    # print(f"Total processing time for AL-RED: {end_time - start_time:.2f} seconds")

    # 3. For GA-BLU
    # start_time: float = time.perf_counter()
    # generate_unique_ids(
    #     part_category="GA",
    #     cap_color_codes=["BLU"],
    #     special_code="",
    #     max_generate_limit=100,
    #     is_debug_mode=True,
    # )
    # end_time: float = time.perf_counter()
    # print(f"Total processing time for GA-BLU: {end_time - start_time:.2f} seconds")

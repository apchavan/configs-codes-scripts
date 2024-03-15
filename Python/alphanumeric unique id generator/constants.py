import os

# TODO: Update below options before deploying on production server.

IS_USING_GOOGLE_SHORT_LINK_DEV_API: bool = True
""" Whether to use the Google's short link API endpoint from `Dev` subscription or `Prod` subscription. """

IS_DASH_DEBUG_MODE: bool = True
""" Whether or not run the Dash application in debug mode. """

HOST_ADDRESS: str = "127.0.0.1"
""" Host IP address of the computer where the Dash application is running. """

DASH_PORT_NO: int = 44667
""" Port number for the Dash application. """

MAX_UNIQUE_ID_GENERATION_LIMIT: int = 2_00_000
""" Maximum per 24 hours limit of Google's short link API endpoint. """

GOOGLE_API_REQUESTS_PER_SECOND: int = 5
""" Maximum per second limit of Google's short link API endpoint. """

DEFAULT_ALPHA_NUM_UNIQUE_ID_LENGTH: int = 6
""" Default length of unique ID characters to be considered during generation process. """

APP_NAME: str = "Alphanumeric Unique ID Generator"
APP_VERSION: str = "0.1"
TVS_TEXT_RGBA_COLOR: str = "rgba(41, 58, 128, 1.0)"

# ID_GENERATION_TRACKING_DATETIME_FORMAT: str = f"%d/%b/%Y %I:%M:%S.%f %p %Z(%z)"
ID_GENERATION_TRACKING_DATETIME_FORMAT: str = f"%d/%b/%Y %I:%M:%S.%f %p"
ID_GENERATION_TRACKING_CSV_FILENAME: str = "id_generation_tracking.csv"

# Path to store data files needed for application internally.
INTERNAL_DATA_DIRPATH: str = os.path.join(
    "Internal_Data",
)
# Overwrite with storage account path when running in non-debug or production.
if not IS_DASH_DEBUG_MODE:
    # INTERNAL_DATA_DIRPATH = ""
    pass

# Path to store secret key files needed to generate the encrypted encoded code.
SECRET_KEYS_DIR_PATH: str = os.path.join(INTERNAL_DATA_DIRPATH, "Secret_Keys")
if not IS_DASH_DEBUG_MODE:
    # SECRET_KEYS_DIR_PATH = ""
    pass

# Path to store files containing alpha-numeric digit length for unique ID.
ALPHA_NUM_DIGIT_LEN_DIR_PATH: str = os.path.join(
    INTERNAL_DATA_DIRPATH, "Alpha_Numeric_Digit_Lengths"
)
if not IS_DASH_DEBUG_MODE:
    # ALPHA_NUM_DIGIT_LEN_DIR_PATH = ""
    pass

# Path to store resulting Excel files.
RESULT_EXCEL_DIRPATH: str = os.path.join(
    "Result",
)
if not IS_DASH_DEBUG_MODE:
    # RESULT_EXCEL_DIRPATH = ""
    pass

# Path to store files for tracking and indexing data using Elasticsearch.
TRACKING_INDEXING_DIRPATH: str = os.path.join(
    "Track_Unique_IDs",
)
if not IS_DASH_DEBUG_MODE:
    # TRACKING_INDEXING_DIRPATH = ""
    pass

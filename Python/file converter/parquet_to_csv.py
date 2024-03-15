"""
    Custom module that can read `.parquet` files and convert, store them as `.csv` files  by following below steps:

    1. The `parquet_base_dir_path` directory is the parent directory which contains sub-directories having parquet files.

    2. Based on sub-directory timestamps, the program selects the newest sub-directory.

"""

import os
import pathlib
import time
import pandas as pd

cpu_time_start: float = time.perf_counter()
wall_time_start: float = time.time()

# Base directory path.
parquet_base_dir_path: str = "/PATH/TO/BASE_PARENT_DIRECTORY"  # TODO: Change this path.

# Current date sub-directory path.
parquet_current_date_dir_path_list: list = sorted(
    pathlib.Path(parquet_base_dir_path).iterdir(),
    key=os.path.getmtime,
    reverse=True,
)

# Current timestamp nested sub-directory path.
parquet_current_timestamp_dir_path_list: list = sorted(
    pathlib.Path(parquet_current_date_dir_path_list[0]).iterdir(),
    key=os.path.getmtime,
    reverse=True,
)

# List of all files stored in current timestamp sub-directory.
parquet_files_path_list: list = sorted(
    pathlib.Path(parquet_current_timestamp_dir_path_list[0]).iterdir(),
    key=os.path.getmtime,
    reverse=False,
)

# Directory tore output CSV files.
csv_dir_location: str = "/PATH/TO/OUTPUT_CSV_DIRECTORY"  # TODO: Change this path.
total_files_processed: int = 0

for parquet_posixpath in parquet_files_path_list:
    if parquet_posixpath.is_dir() or not os.path.join(parquet_posixpath).endswith(
        ".parquet"
    ):
        # Skip iteration if the path is directory or not a parquet file.
        continue

    pd_dataframe: pd.DataFrame = pd.read_parquet(os.path.join(parquet_posixpath))

    csv_file_name: str = (
        os.path.join(parquet_posixpath).split("/")[-1].split(".")[0] + ".csv"
    )

    pd_dataframe.to_csv(
        os.path.join(csv_dir_location, csv_file_name),
        index=False,
        mode="w",
    )
    total_files_processed += 1

print(
    f"\n(I) Ported {total_files_processed} parquet files to CSV & stored at '{csv_dir_location}'. (CPU time: {time.perf_counter() - cpu_time_start} sec, Wall time: {time.time() - wall_time_start} sec)",
    end="\n\n",
)

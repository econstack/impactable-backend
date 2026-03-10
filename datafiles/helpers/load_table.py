"""loads a df into the datafiles table"""

from typing import Union
from pathlib import Path

import pandas as pd

from config import DATA_BASE_DIR
from helpers.pandas_helpers import dataframe_info

from datafiles.models import Datafile
from datafiles import logger


def make_save_test_datafile_table() -> Path:
    """Exports the current datafiles table into a dataframe and is saved as a parquet file in default testing location."""
    # set the test file path
    fp = Path(DATA_BASE_DIR, "tests", "datafiles_table.parquet")
    # pull the datafile table into a dataframe
    dataf = Datafile.objects.all().values()
    df = pd.DataFrame(dataf)
    # save dataframe to parquet file
    df.to_parquet(fp)
    logger.debug(f"make_save_test_datafile_table - saved {len(df)} rows to {fp}")
    return fp


def load_test_datafile_table() -> int:
    """loads a df into the datafiles table in the database and returns the number of rows loaded. The file path should be a parquet file."""
    # set the test file path
    fp = Path(DATA_BASE_DIR, "tests", "datafiles_table.parquet")
    return load_table(fp=fp)


def load_table(fp: Union[Path, None] = None) -> int:
    """loads a df into the datafiles table in the database and returns the number of rows loaded. if the file path is not provided, loads the test datafile. The file path should be a parquet file."""
    if fp is None:
        fp = Path(DATA_BASE_DIR, "tests", "datafiles_table.parquet")

    # read in the data
    df = pd.read_parquet(fp)
    # logger.debug(f"df.info():\n{dataframe_info(df)}")

    # load the data into the datafiles table
    # note: using the custom udpate_or_create method will need to pass a df and a new file_name may be created which will not match the file name in the datafile storage
    for i, row in df.iterrows():
        _ = Datafile.objects.create(
            name=row["name"],
            contact=row["contact"],
            file_type=row["file_type"],
            description=row["description"],
            file=row["file"],
            sheet_name=row.get("sheet_name", None),
            header_row=row.get("header_row", None),
        )
    logger.debug(f"load_table - loaded {len(df)} rows from {fp}")
    return len(df)

import pandas as pd
from pathlib import Path
from config import MEDIA_BASE_DIR

from ..models import Datafile
from datafiles import logger


def read_datafile(raw_file: Datafile) -> pd.DataFrame:
    """Read in the data from the raw file and return a dataframe."""
    logger.debug(f"raw_file.file: {raw_file.file}")
    logger.debug(f"file exists: {raw_file.file.path if raw_file.file else 'No file'}")
    if raw_file.file:
        ext = raw_file.file.name.split(".")[-1]
        if ext == "csv":
            # convert file string to path
            fp = Path(MEDIA_BASE_DIR, raw_file.file.name)
            # df = pd.read_csv(raw_file.file)
            df = pd.read_csv(fp, keep_default_na=False, na_values=[""])
        elif ext == "xlsx":
            sheet_name = raw_file.sheet_name
            header_row = raw_file.header_row
            # logger.debug(f"sheet_name: {sheet_name}, header_row: {header_row}")
            if sheet_name:
                df = pd.read_excel(
                    raw_file.file,
                    sheet_name=sheet_name,
                    header=header_row,
                    keep_default_na=False,
                    na_values=[""],
                )
            else:
                df = pd.read_excel(
                    raw_file.file,
                    header=header_row,
                    keep_default_na=False,
                    na_values=[""],
                )
        elif ext == "parquet":
            df = pd.read_parquet(raw_file.file)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    else:
        raise ValueError("No file associated with the Datafile instance.")

    logger.debug(f"df.shape: {df.shape}")
    return df

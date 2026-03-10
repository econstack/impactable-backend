"""clean up raw datafiles and save as cleaned datafiles in parquet format"""

# todo: implement this function, find all raw files and if they have not been cleaned, then apply the cleaning function and save as cleaned files

from pathlib import Path

# from django.core.files import File
from pprint import pformat

import pandas as pd

from config import MEDIA_BASE_DIR
from helpers.pandas_helpers import (
    standardize_df_col_names,
    dataframe_info,
    base_clean_dataframe,
)

from datafiles import logger
from datafiles.helpers.files_io import read_datafile
from datafiles.models import Datafile, get_upload_path


def clean_all_raw_files() -> list[Datafile]:
    """clean up all raw files that have not been cleaned yet. Returns list of cleaned datafiles."""
    # find all raw files without a reference for 'cleaned'
    raw_files = Datafile.objects.filter(file_type=Datafile.FileType.RAW, cleaned=None)
    logger.debug(f"raw_files: {pformat(list(raw_files))}")
    # for each raw file, apply the cleaning function
    cleaned_datafiles = []
    for raw_file in raw_files:
        cleaned_datafiles.append(clean_raw_file(raw_file))
    return cleaned_datafiles


def clean_raw_file(raw_file: Datafile) -> Datafile:
    """clean up the raw file and save as a cleaned file. Returns the instance of the cleaned file."""
    # read in the raw data file
    df = read_datafile(raw_file)
    # logger.debug(f"raw_file: {raw_file}, df:\n{dataframe_info(df)}")

    # clean up the dataframe
    df = base_clean_dataframe(df)
    # logger.debug(f"df.info:\n{dataframe_info(df)}")

    # save the cleaned file as a parquet file and create instance of the cleaned file
    cleaned_datafile_name = f"{raw_file.name}-cleaned"

    # create the instance of the cleaned file
    cleaned_file, _ = Datafile.objects.update_or_create(
        df=df,
        file_name=f"{cleaned_datafile_name}.parquet",
        name=cleaned_datafile_name,
        file_type=Datafile.FileType.CLEANED,
        description=f"cleaned version of {raw_file.name}: {raw_file.description}",
        defaults={
            "raw_source": raw_file,
        },
    )

    return cleaned_file

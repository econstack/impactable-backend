import os
from pathlib import Path
from typing import List, Dict, Tuple, Any
from string import ascii_lowercase
from typing import TYPE_CHECKING

import openpyxl
import pandas as pd
import pantab

if TYPE_CHECKING:
    from datafiles.models import Datafile

from config import logger, DATA_BASE_DIR, MEDIA_BASE_DIR
from helpers.string_helpers import recode_list_loweralphanumeric
from helpers.pandas_helpers import dataframe_info


def list_files(directory):
    """returns a list of csv and excel files in the directory"""
    files = [
        f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))
    ]
    # logger.debug(f"files: {files}")
    files = [f for f in files if ".csv" in f or ".xlsx" in f]
    return files


def check_image_exists(excel_file: Path, sheet_name: str, cell: str) -> bool:
    """checks if an image exists in a cell in an excel file. Returns True if the image exists and False if it does not. Note cell is a string with the column letter and row number, eg 'A1' (note: column letters limited to A-Z (no AA, AB, etc.)). todo: add support for multiple letter columns for the cell."""
    workbook = openpyxl.load_workbook(excel_file)
    sheet = workbook[sheet_name]
    images = [image for image in sheet._images]
    # logger.debug(f"images: {images}")
    for image in images:
        row = image.anchor._from.row
        col = image.anchor._from.col
        logger.debug(f"cell0:{cell[0]}, cell1:{cell[1:]}")
        target_row = int(cell[1:]) - 1
        # get dict of lower case letters to position in alphabet
        LETTERS = {
            letter: index for index, letter in enumerate(ascii_lowercase, start=1)
        }
        target_col = LETTERS[cell[0].lower()] - 1
        # logger.debug(f"test row,col: {row, col}")
        # logger.debug(f"target row,col: {target_row, target_col}")

        # Check if the cell contains an image
        if row == target_row and col == target_col:
            return True
        else:
            continue

    # no matches fond
    return False


def num_images_excel_sheet(excel_file: Path, sheet_name: str) -> int:
    """checks the number of images in a sheet in an excel file. Returns the number of images in the sheet."""
    workbook = openpyxl.load_workbook(excel_file)
    sheet = workbook[sheet_name]
    images = [image for image in sheet._images]
    return len(images)


def read_csv(file_path: Path, **kwargs) -> pd.DataFrame:
    """reads in a csv file and returns a pandas dataframe with standardized col names (only alphanumeric and lowercase with dashes)"""
    options = {}
    if "keep_underscore" in kwargs:
        kwargs.pop("keep_underscore")
        options["keep_underscore"] = True
    if "keep_dash" in kwargs:
        kwargs.pop("keep_dash")
        options["keep_dash"] = True

    df = pd.read_csv(file_path, keep_default_na=False, na_values=[""], **kwargs)
    df.rename(
        columns=recode_list_loweralphanumeric(
            list(df.columns),
            keep_dash=options.get("keep_dash", False),
            keep_underscore=options.get("keep_underscore", False),
        ),
        inplace=True,
    )
    return df


def read_excel(file_path: Path, **kwargs) -> pd.DataFrame:
    """reads in an excel file and returns a pandas dataframe with standardized col names (only alphanumeric and lowercase with dashes)"""
    options = {}
    if "keep_underscore" in kwargs:
        kwargs.pop("keep_underscore")
        options["keep_underscore"] = True
    if "keep_dash" in kwargs:
        kwargs.pop("keep_dash")
        options["keep_dash"] = True

    df = pd.read_excel(file_path, keep_default_na=False, na_values=[""], **kwargs)

    df.rename(
        columns=recode_list_loweralphanumeric(
            list(df.columns),
            keep_dash=options.get("keep_dash", False),
            keep_underscore=options.get("keep_underscore", False),
        ),
        inplace=True,
    )
    return df


def write_dataframes_excel(file_path, dataframes: Dict[str, pd.DataFrame]) -> List[str]:
    """writes a dictionary of dataframes to an excel file and returns a list of the sheet names in the excel file where the dataframes is a dict with the sheet name as the key and the dataframe as the value"""
    sheets = []
    with pd.ExcelWriter(file_path) as writer:
        for sheet_name, df in dataframes.items():
            if isinstance(df, pd.DataFrame):
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                sheets.append(sheet_name)

    return sheets


def make_csv_from_parquet(parquet_file: Path, csv_file: Path = None) -> Path:
    """reads in a parquet file and writes it to a csv file with the same name in the same directory and returns the path to the csv file. Option to provide a specific csv file path."""
    df = pd.read_parquet(parquet_file)
    if csv_file is None:
        csv_file = parquet_file.with_suffix(".csv")
        # logger.debug(f"csv_file: {csv_file}, parquet_file: {parquet_file}")
    df.to_csv(csv_file, index=False)
    return csv_file


def make_csv_from_parquet_dir(
    parquet_dir: Path,
    csv_dir: Path = None,
    tableau_only: bool = False,
    must_contain: str = "",
) -> List[Path]:
    """reads in all the parquet files in a directory and writes them to csv files with the same name in the same directory and returns the list of paths to the csv files. Option to provide a specific csv directory.
    args:
    - parquet_dir: Path to the directory with the parquet files
    - csv_dir: Path to the directory to save the csv files. If None, saves to the same directory as the parquet files.
    - tableau_only: If True, only converts parquet files with 'tableau' in the name
    - must_contain: If provided, only converts parquet files with the string in the filename
    """
    # logger.debug(f"csv_dir: {csv_dir}")
    csv_files = []
    # find all parquet files in the directory
    parquet_files = list(parquet_dir.glob("*.parquet"))
    if tableau_only:
        parquet_files = [f for f in parquet_files if "tableau" in f.name]
    if must_contain:
        must_contain = str(must_contain)
        parquet_files = [f for f in parquet_files if must_contain in f.name]
    # logger.debug(f"parquet_files: {parquet_files}")

    for parquet_file in parquet_files:
        parquet_file_path = Path(parquet_dir, parquet_file)
        if csv_dir is None:
            csv_file = make_csv_from_parquet(parquet_file_path)
        else:
            csv_fp = csv_dir / parquet_file.with_suffix(".csv").name
            # logger.debug(f"csv_file: {csv_fp}, parquet_file: {parquet_file}")
            csv_file = make_csv_from_parquet(parquet_file, csv_fp)
        csv_files.append(csv_file)
    return csv_files


def make_hyper_from_parquet(
    parquet_file: Path, hyper_file: Path = None
) -> Tuple[Path, str]:
    """reads in a parquet file and writes it to a hyper file with the same name in the same directory and returns the path to the hyper file. Option to provide a specific hyper file path."""
    df = pd.read_parquet(parquet_file)
    if hyper_file is None:
        hyper_file = parquet_file.with_suffix(".hyper")
        # logger.debug(f"hyper_file: {hyper_file}, parquet_file: {parquet_file}")
    table_name = hyper_file.name.split(".")[0]
    pantab.frame_to_hyper(df, hyper_file, table=table_name)
    # df.to_csv(hyper_file, index=False)
    return (hyper_file, table_name)


def make_hyper_from_parquet_dir(
    parquet_dir: Path,
    hyper_file: Path,
    tableau_only: bool = False,
    must_contain: str = "",
) -> Dict[str, Any]:
    """reads in all the parquet files in a directory and writes them to a hyperfile with the filenames as the table names. Returns a dict with the path to the hyper file and a list of the tables created.
    Return keys:
    - "hyper_file": Path to the hyper file
    - "tables": List of the table names
    args:
    - parquet_dir: Path to the directory with the parquet files
    - hyper_file: Path to the hyper file to save the data
    - tableau_only: If True, only converts parquet files with 'tableau' in the name
    - must_contain: If provided, only converts parquet files with the string in the filename
    """

    # find all parquet files in the directory
    parquet_files = list(parquet_dir.glob("*.parquet"))
    # logger.debug(f"parquet_files: {parquet_files}")
    if tableau_only:
        parquet_files = [f for f in parquet_files if "tableau" in f.name]
    if must_contain:
        must_contain = str(must_contain)
        parquet_files = [f for f in parquet_files if must_contain in f.name]

    df_dct = {}
    for parquet_file in parquet_files:
        df = pd.read_parquet(parquet_file)
        logger.debug(f"Original DataFrame from {parquet_file}:\n{dataframe_info(df)}")
        df = clean_df_for_hyper(df)
        logger.debug(f"Processed DataFrame for {parquet_file}:\n{dataframe_info(df)}")
        df_dct[parquet_file.name] = df

    pantab.frames_to_hyper(df_dct, hyper_file)

    return {"hyper_file": hyper_file, "tables": [k for k in df_dct.keys()]}


def clean_df_for_hyper(df: pd.DataFrame) -> pd.DataFrame:
    """cleans the dataframe for hyper. Removes any columns with all nulls and removes any columns with all empty strings."""
    df = df.fillna(pd.NA)  # Replace null values with 0 or any other appropriate value
    df = df.convert_dtypes()

    # Convert unsupported data types to supported ones
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]):
            df[col] = df[col].astype(str)
        elif isinstance(df[col].dtype, pd.CategoricalDtype):
            df[col] = df[col].astype(str)
        elif pd.api.types.is_bool_dtype(df[col]):
            df[col] = df[col].astype("boolean")
        elif pd.api.types.is_float_dtype(df[col]):
            df[col] = df[col].astype("Float64")
        elif pd.api.types.is_integer_dtype(df[col]):
            df[col] = df[col].astype("Int64")
    return df


def make_save_tableau_hyper(datafiles: Dict[str, "Datafile"], hyper_name: str) -> Path:
    """makes a tableau hyper file from the parquet files from datafiles. Returns the path to the saved hyper file. The names of the tableau tables are the keys to the datafiles dict."""
    from datafiles.helpers.files_io import read_datafile

    hyper_dct = {}

    for name, datafile in datafiles.items():

        # read in the parquet file
        df = read_datafile(datafile)
        # clean the dataframe for hyper
        df = clean_df_for_hyper(df)
        # update dict for hyper with dataframe
        hyper_dct[name] = df

    fp = Path(DATA_BASE_DIR, "ETL", "tableau", f"{hyper_name}.hyper")
    pantab.frame_to_hyper(hyper_dct, fp)

    # convert to path and return
    fp = Path(MEDIA_BASE_DIR, str(datafile.file))

    return fp

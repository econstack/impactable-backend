from typing import List, Dict, Union

from pathlib import Path

import pandas as pd
import numpy as np

from helpers.string_helpers import (
    standardize_loweralphanumeric,
    recode_numeric,
)
from config import logger, DATA_BASE_DIR
from helpers.string_helpers import recode_boolean


def cols_delta(df: pd.DataFrame) -> List[str]:
    """Given dataframe with one or more rows, returns the names of columns where the data is different across rows"""
    return df.columns[df.nunique() > 1].tolist()


def clean_blanks(df: pd.DataFrame) -> pd.DataFrame:
    """replaces all blank strings with np.nan in a dataframe"""
    df_ = df.copy()
    df_.replace(r"^\s*$", np.nan, regex=True, inplace=True)
    return df_


def dataframe_info(df: pd.DataFrame):
    """returns df.info() as a dataframe with the following columns:
    - 'name': the column name
    - 'non-nulls': the number of non-null values in the column
    - 'nulls': the number of null values in the column
    - 'type': the data type of the column
    """
    return pd.DataFrame(
        {
            "name": df.columns,
            "non-nulls": len(df) - df.isnull().sum().values,  # type: ignore
            "nulls": df.isnull().sum().values,
            "type": df.dtypes.values,
            # "dtype": df.apply(type),
        }
    )


def standardize_df_col_names(
    df_cols: Union[List[str], pd.Index], separator=" "
) -> Dict[str, str]:
    """returns a dict of {old_col_names: standardized column names} for a list of column names with optional separator (default is ' ') where the standardized column names are lower case and alphanumeric only (no special characters) and separated by the separator. Main use case:

    df.rename(columns=standardize_df_col_names(df.columns), inplace=True)
    """
    if isinstance(df_cols, pd.Index):
        df_cols = list(df_cols)

    return {x: standardize_loweralphanumeric(x, separator=separator) for x in df_cols}


def save_dataframes_to_excel(
    filepath: Path,
    dfs: Dict[str, pd.DataFrame],
) -> Path:
    """saves a set of dataframes to excel file as sheets as given by dfs dict with structure: {sheetname: dataframe}. Returns the filepath as string.
    Args:
    - filepath: Path to save the excel file (must end in .xlsx)
    - dfs: dict of {sheetname: dataframe} to save to the excel file
    """

    # validation that the number of sheets is less than 50, else raise error
    if len(dfs.keys()) > 50:
        raise ValueError(
            f"Number of sheets: {len(dfs.keys())} is greater than 50. Excel file save is limited to 50 sheets maximum."
        )
    # save to excel
    with pd.ExcelWriter(filepath, engine="xlsxwriter") as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    return filepath


def base_clean_dataframe(
    df_raw: pd.DataFrame, standardize_col_names: bool = True
) -> pd.DataFrame:
    """cleans up the dataframe by:
    - standardizing the column names to lower alphanumeric
    - applying convert_dtypes to the dataframe
    - converting all object columns to string, and filling nulls with ""
    - if there is a project id column, dropping all rows without a valid project id (ie. anything that is not a number or cannot be converted to a number)
    Cleaned dataframe cols will all be allowed to be saved as parquet
    Returns the cleaned dataframe
    """
    df = df_raw.copy()

    # clean up the col names to be standardized
    if standardize_col_names:
        df.rename(
            columns=standardize_df_col_names(list(df.columns)),
            inplace=True,
        )

    # clean up the data types
    df = df.convert_dtypes()
    # logger.debug(f"df.info:\n{dataframe_info(df)}")

    # find all the object cols and fill as strings with "" for nulls
    object_cols = df.select_dtypes(include=[object]).columns
    # object_cols_ = df.select_dtypes(include=[object])
    # logger.debug(f"object_cols: {object_cols}, object_cols_: {object_cols_}")

    # if there is a project id col, drop all rows without a valid project id - i.e. it is an int
    if "project id" in df.columns:
        df["project id"] = df["project id"].apply(lambda x: recode_numeric(x))
        # drop all rows without a valid project id
        df = df[df["project id"].notna()]
        # convert the project id to int
        df["project id"] = df["project id"].astype(int)

    for col in object_cols:
        # fill na with empty string
        df[col] = df[col].apply(lambda x: "" if pd.isna(x) else x)
        # convert to string
        df[col] = df[col].astype(str)

    # convert the object cols to string
    df = df.convert_dtypes()
    return df


def update_data_col(
    ds: pd.Series,
    original_data_col: str,
    update_data_col: str,
    data_type: str = "float",
    comment_col: str = "",
):
    """updates a dataframe (with apply) or series for a specified data col of the original and updated data. Will replace original if update is non-empty and is the same type as the original.

    args:
    - ds: row of dataframe
    - original_data_col: label for column with the original data
    - update_data_col: label for column with the updated data
    - data_type: expected data type for the data columns - must be a valid python type (e.g. int, float, str, bool). type str will allow any data type. Default is float.
    - comment_col: label for column with the comment to add if update is made (optional). If not provided, no comments will be added.
    """
    # verify that data_type is valid
    vali_data_types = {"int": int, "float": float, "str": str, "bool": bool}
    if data_type not in vali_data_types:
        raise ValueError(
            f"Invalid data_type '{data_type}'. Must be one of {list(vali_data_types.keys())}."
        )

    ds_ = ds.copy()

    # check that the comment col exists
    if comment_col != "" and comment_col not in ds_.index:
        raise ValueError(
            f"Comment column '{comment_col}' does not exist in the dataframe/series."
        )

    try:
        if data_type == "float" or data_type == "int":
            updated_value = recode_numeric(ds_[update_data_col])
            if pd.notna(updated_value):
                updated_value = float(updated_value)
        elif data_type == "bool":
            updated_value = recode_boolean(ds_[update_data_col])
        else:  # case: data_type is str
            updated_value = ds_[update_data_col]

        have_valid_update = pd.notna(updated_value)
        if data_type == "str":
            have_valid_update = updated_value != ""

        # case: have update value
        if have_valid_update:

            # logger.debug(
            #     f"update_valued:'{updated_value}' for col:'{update_data_col}' and original value:'{ds_[original_data_col]}'"
            # )

            # update is available and types match
            if isinstance(updated_value, vali_data_types[data_type]):
                ds_[original_data_col] = updated_value

            # case: if have update but type mismatch, then add error statement to comment col if exists
            elif (
                not isinstance(updated_value, vali_data_types[data_type])
            ) and pd.notna(comment_col):
                comment = f"Type mismatch for '{original_data_col}': data type {vali_data_types[data_type]}, updated type {type(updated_value)}. No update made with value {updated_value}."
                if pd.isna(ds.get(comment_col)):
                    ds_[comment_col] = comment
                else:
                    ds_[comment_col] += f" {comment}"

            # else do nothing - (have original value and update value is missing) or (type mismatch and no comment col)
            elif (
                not isinstance(updated_value, vali_data_types[data_type])
                and comment_col == ""
            ):
                # logger.debug(
                #     f"Type mismatch for '{original_data_col}': data type {vali_data_types[data_type]}, updated type {type(updated_value)}. No update made with value {updated_value}. No comment column provided."
                # )
                pass

            # all other cases
            else:
                # logger.debug(
                #     f"Update error for '{original_data_col}': data type {vali_data_types[data_type]}, updated type {type(updated_value)}. No update made with value '{updated_value}' for original data '{original_data_col}'. No comment column provided!"
                # )
                pass
        # case: invalid update value and write to comment col
        elif not have_valid_update and comment_col != "" and comment_col in ds_.index:
            if pd.isna(ds_[update_data_col]) or (
                isinstance(updated_value, str) and updated_value == ""
            ):
                pass
            else:
                # case: invalid update value - write error message to comment col if exists
                error_msg = f"No valid update value for col '{update_data_col}' with value '{ds_[update_data_col]}' for original data '{ds_[original_data_col]}' and expected data type:'{data_type}'. No update made. "
                if pd.notna(comment_col):
                    if ds.get(comment_col) == "":
                        ds_[comment_col] = error_msg
                    else:
                        ds_[comment_col] += f" {error_msg}"

        # case: invalid update value and no comment col - log to debug
        else:
            error_msg = f"No valid update value for col '{update_data_col}' with value '{ds_[update_data_col]}' for original data '{ds_[original_data_col]}' and expected data type:'{data_type}'. No update made. "
            logger.debug(error_msg)

    except Exception as e:
        error_msg = f"No valid update value for col '{update_data_col}' with value '{ds_[update_data_col]}' for original data '{ds_[original_data_col]}' and expected data type:'{data_type}'. No update made. "
        logger.debug(error_msg)
        raise e

    return ds_

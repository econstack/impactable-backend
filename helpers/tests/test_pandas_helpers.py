# from unittest import TestCase
import pytest
import os
from pathlib import Path
from helpers.pandas_helpers import (
    base_clean_dataframe,
    update_data_col,
    save_dataframes_to_excel,
    standardize_df_col_names,
    dataframe_info,
)
from config import logger, DATA_BASE_DIR

import pandas as pd


def test_base_clean_dataframe():
    # set up test dataframe with a few nulls for a string column and an integer column wtih a few nulls
    df = pd.DataFrame(
        {
            "string_col": ["a", "b", "c", "d", None, ""],
            "int_col": [1, 2, 3, None, 5, 6],
        }
    )
    # logger.debug(f"df:\n{dataframe_info( df)}")
    # logger.debug(f"df:\n{df}")

    # there should be no nulls in the cleaned dataframe for the string column but there should be for the int column and the data types should be string and int64 respectively
    df_clean = base_clean_dataframe(df)
    # logger.debug(f"df_clean:\n{dataframe_info( df_clean)}")
    # logger.debug(f"df_clean:\n{df_clean}")

    assert df_clean["int col"].isnull().sum() == 1
    assert df_clean["string col"].dtype == "string"
    assert df_clean["int col"].dtype == "Int64"

    # save the cleaned dataframe to a parquet file and should not raise error
    fp = Path(DATA_BASE_DIR, "temp", "test_base_clean_dataframe.parquet")
    fp.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_parquet(fp)
    os.remove(fp)


def test_update_data_col():
    # set up test dataframe with original_data, update_data, comment_data columns
    test_comment = "old comment."
    df = pd.DataFrame(
        {
            "original_data": [10, pd.NA, 10, 20, pd.NA],
            "update_data": [15, 15, pd.NA, "wrong type", "wrong type"],
            "comment_data": ["", "", test_comment, test_comment, ""],
        }
    )

    # apply update_data_col to each row
    df_out = df.apply(
        lambda row: update_data_col(
            row, "original_data", "update_data", "float", comment_col="comment_data"
        ),
        axis=1,
    )

    expected_original_data_values = [15.0, 15.0, 10.0, 20.0, pd.NA]

    # check that the values are as expected
    for i, val in enumerate(expected_original_data_values):
        if pd.isna(val):
            assert pd.isna(df_out.iloc[i]["original_data"])
        else:
            assert df_out.iloc[i]["original_data"] == val

    # check that the comments are as expected, nulls for first 2 rows, test comment for 3rd row, and 4th row should have test comment and then some additional text, and last row should be non-empty string
    assert df_out.iloc[0]["comment_data"] == ""
    assert df_out.iloc[1]["comment_data"] == ""
    assert df_out.iloc[2]["comment_data"] == test_comment
    assert test_comment in df_out.iloc[3]["comment_data"]
    assert len(df_out.iloc[3]["comment_data"]) > len(test_comment)
    assert df_out.iloc[4]["comment_data"] != ""


def test_update_data_col_case_NA():
    # set up test dataframe with original_data, update_data, comment_data columns
    # have cases: NA for original data, NA for update data, and both nulls
    test_comment = "old comment."
    df = pd.DataFrame(
        {
            "original_data": [pd.NA, 10, pd.NA],
            "update_data": [15, pd.NA, pd.NA],
            "comment_data": ["", "", test_comment],
        }
    )

    # apply update_data_col to each row
    df_out = df.apply(
        lambda row: update_data_col(
            row, "original_data", "update_data", "float", comment_col="comment_data"
        ),
        axis=1,
    )
    logger.debug(f"df_out:\n{dataframe_info(df_out)}")
    logger.debug(f"df_out:\n{df_out}")

    expected_original_data_values = [15.0, 10.0, pd.NA]

    # check that the values are as expected
    for i, val in enumerate(expected_original_data_values):
        if pd.isna(val):
            assert pd.isna(df_out.iloc[i]["original_data"])
        else:
            assert df_out.iloc[i]["original_data"] == val


def test_update_data_col_case_missing_comment_col():
    # set up test dataframe with original_data, update_data columns but no comment_data column
    df = pd.DataFrame(
        {
            "original_data": [10, pd.NA, 10],
            "update_data": [15, 15, pd.NA],
        }
    )

    # apply update_data_col to each row and expect a ValueError because comment_col does not exist
    with pytest.raises(ValueError):
        df.apply(
            lambda row: update_data_col(
                row,
                "original_data",
                "update_data",
                "float",
                comment_col="comment_data",
            ),
            axis=1,
        )


def test_update_data_col_case_str():
    # set up test dataframe with original_data, update_data, comment_data columns
    # have cases: update data, no original data, no update data, wrong type update data, update data with unmatched case (should update), and both nulls
    test_comment = "old comment."
    df = pd.DataFrame(
        {
            "original_data": ["low", "", "medium", "high", "low", ""],
            "update_data": ["Medium", "High", "", 44, "Low", ""],
            "comment_data": ["", "", test_comment, test_comment, "", ""],
        }
    )

    # apply update_data_col to each row
    df_out = df.apply(
        lambda row: update_data_col(
            row, "original_data", "update_data", "str", comment_col="comment_data"
        ),
        axis=1,
    )
    # logger.debug(f"df_out:\n{dataframe_info(df_out)}")
    # logger.debug(f"df_out:\n{df_out}")

    expected_original_data_values = ["Medium", "High", "medium", "high", "Low", ""]

    # check that the values are as expected
    for i, val in enumerate(expected_original_data_values):
        assert df_out.iloc[i]["original_data"] == val, f"i={i}, val={val}"

    # check that the comments are as expected
    assert df_out.iloc[0]["comment_data"] == ""
    assert df_out.iloc[1]["comment_data"] == ""
    assert df_out.iloc[2]["comment_data"] == test_comment
    assert test_comment in df_out.iloc[3]["comment_data"]
    assert len(df_out.iloc[3]["comment_data"]) > len(test_comment)

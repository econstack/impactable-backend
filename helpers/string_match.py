"""functions for string matching, looking first for exact match in list, then for standardized match in list, and finally for fuzzy match in list."""

from typing import List
from rapidfuzz import fuzz

import pandas as pd
from config import logger
from helpers.pandas_helpers import dataframe_info


def _get_fuzzy_match_scores(names_list: List[str], test_name: str) -> pd.DataFrame:
    """Given a list of names and a test name, return a dataframe with the names and their fuzzy match scores against the test name. Adds column 'score' (floats) in [0,100]"""
    scores = [fuzz.ratio(name, test_name) for name in names_list]
    df = pd.DataFrame({"name": names_list, "score": scores})
    return df


def get_best_string_match(
    names_list: List[str], test_name: str, min_score: float = 70, min_gap: float = 8
) -> str:
    """Given a list of names and a test name, return the best matching name based on fuzzy string matching.

    args:
    - names_list: A list of names to match against.
    - test_name: The name to match.
    - min_score: The minimum score for a match to be considered (default is 70).
    - min_gap: The minimum gap between the best and second-best match scores (default is 8 which allows for some flexibility, but may not be sufficient in all cases). Ideally, it should be a function of the min_score. If min_score is higher, min_gap should be lower, i.e. if we have multiple low confidence match, we should be more strict about the gap to select one.
    """
    df = _get_fuzzy_match_scores(names_list, test_name)
    # logger.debug(f"df.info():{dataframe_info(df)}")

    # filter out for min_score and sort by score
    df = df[df["score"] >= min_score]
    df = df.sort_values("score", ascending=False)

    # make sure we have at least one match
    if df.empty:
        return ""
    best_match = df.iloc[0]
    # assign second best match if it exists
    second_best_match = df.iloc[1] if len(df) > 1 else None

    # logger.debug(f"best_match: \n{best_match}")
    # logger.debug(f"second_best_match: \n{second_best_match}")

    # if have second match, see if gap is large enough, if second match missing, assume it is zero
    test_gap = (
        best_match["score"] - second_best_match["score"]
        if second_best_match is not None
        else best_match["score"]
    )
    # logger.debug(f"test_gap: {test_gap}, min_gap: {min_gap}")

    if test_gap >= min_gap:
        return best_match["name"]
    return ""

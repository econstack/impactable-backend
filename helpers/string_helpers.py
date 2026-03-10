from typing import List, Dict, Union, Any, Type
import re
from math import log10, floor
from numpy import isnan, number
from pandas import Index
from pandas._libs.missing import NAType
import pandas as pd

from config import logger


def recode_boolean(
    value, default_null: Union[NAType, bool] = pd.NA, recode_yes_no: bool = False
) -> Union[bool, NAType, str]:
    """returns True/False if value can be interpreted as boolean, else returns default_null (default is pd.NA) - this is to be used when recoding boolean values from strings or other types where there may be some ambiguity in the values (e.g. "Yes", "No", "Y", "N", 1, 0, True, False, etc.). Have included "-1" as a falsy value because some datasets use -1 to indicate "no" or "false".

    If recode_yes_no is True, then we will recode all truthy values as "yes" and all falsy values as "no" (use case: some datasets have yes/no values). If recode_yes_no is True, then the function will return "yes"/"no" instead of True/False.
    """
    if isinstance(value, bool):
        return (
            "yes"
            if value and recode_yes_no
            else "no" if not value and recode_yes_no else value
        )
    elif isinstance(value, str):
        value_lower = value.strip().lower()
        if value_lower in ["yes", "y", "true", "1"]:
            return "yes" if recode_yes_no else True
        elif value_lower in ["no", "n", "false", "0", "-1"]:
            return "no" if recode_yes_no else False
    elif isinstance(value, (int, float)):
        if value == 1:
            return "yes" if recode_yes_no else True
        elif value == 0 or value == -1:
            return "no" if recode_yes_no else False
    return default_null


def recode_numeric(string: Any, boolean_true: str = "") -> Union[int, float, None]:
    """Given a string, return the string as a number if it is a number, else return None. Converts booleans to 1/0 if boolean_true is provided. If string is None, return None. If string is already a number, return the number. If string is not a number, return None. If string is a boolean, return 1/0 if boolean_true is provided."""
    # logger.debug(f"recode_numeric: {string}")
    if string is None:
        return None
    elif isinstance(string, str):
        if boolean_true and string.lower() == boolean_true.lower():
            return 1
        elif boolean_true and string.lower() != boolean_true.lower():
            return 0
        # logger.debug(f"string is str: {string}")
        # remove commas from string
        string = string.replace(",", "")
        try:
            return int(string)
        except ValueError:
            # logger.debug(f"string: {string}")
            try:
                return float(string)
            except ValueError:
                return None  # type: ignore
    # case: if already a number, return the number
    elif isinstance(string, (float, int, number)):
        # logger.debug(f"string: {string}")
        return string  # type: ignore
    else:
        # logger.debug(f"string: {string}, type: {type(string)}")
        return None


def recode_alpha(
    string: str,
    keep_dash: bool = False,
    keep_underscore: bool = False,
    keep_caps: bool = False,
) -> Union[str, None]:
    """returns only the alphabetic parts of a string, removing all non-alphabetic characters. Options:
    - keep_dash: keep '-' in string (default = False)
    - keep_underscore: keep '_' in string (default = False)
    - keep_caps: keep words in all caps in string (default = False).
    """
    if string is None:
        return None
    elif isinstance(string, str):
        if keep_dash and keep_underscore:
            s = re.sub(r"[^A-Za-z\-\_. ]+", "", string.strip())
        elif keep_dash and not keep_underscore:
            s = re.sub(r"[^A-Za-z\- ]+", "", string.strip())
        elif keep_underscore and not keep_dash:
            s = re.sub(r"[^A-Za-z\_ ]+", "", string.strip())
        else:
            s = re.sub(r"[^A-Za-z ]+", "", string.strip())
        if keep_caps:
            s = [x if is_all_caps(x) else x.lower() for x in s.split()]
        else:
            s = [x.lower() for x in s.split()]
        # logger.debug(f"string: {string}, s: {s}")
        return " ".join(s)


def standardize_regular_chars(
    string: str, separator: str = " ", replacement: str = ""
) -> str:
    """removes all non regular characters from a string, with option to replaces them with a space or alternative separator (default is null). Also removes all double and multiple spaces between words.

    Expected use: clean up dataframe cells that may contain special characters or non-regular characters
    """
    s = re.sub(
        r"[^A-Za-z0-9 \(\)\-/.,!?\$\%@\$=#&\[\]:;<>\\]+", replacement, string.strip()
    )
    s = s.strip()
    s = re.sub(r"\s+", separator, s)

    return s


def standardize_loweralphanumeric(string: str, separator: str = " ") -> str:
    """removes all non-alphanumeric characters from a string and replaces them with a space (or alternative separator). Also removes all double and multiple spaces between words. Expected use: dataframes column headers or strings that need to be standardized for comparison"""
    # check that string is a str
    if isinstance(string, str) is False:
        return string

    s = re.sub(r"[^A-Za-z0-9 ]+", " ", string.strip())
    s = s.lower().strip()
    s = re.sub(r"\s+", separator, s)

    return s


def recode_loweralphanumeric(
    string: str,
    keep_dash: bool = False,
    keep_underscore: bool = False,
    keep_caps: bool = False,
) -> Union[str, None]:
    """Given a string, keep only the alphanumeric parts of a string and any space (but not \n \t) and transforms all alpha into lowercase - removes all double and multiple spaces between words. Options:
    - keep_dash: keep '-' in string (default = False)
    - keep_underscore: keep '_' in string (default = False)
    - keep_caps: keep words in all caps in string (default = False).
    """
    if string is None:
        return None
    elif isinstance(string, str):
        if keep_dash and keep_underscore:
            s = re.sub(r"[^A-Za-z0-9\-\_ ]+", "", string.strip())
        elif keep_dash and not keep_underscore:
            s = re.sub(r"[^A-Za-z0-9\- ]+", "", string.strip())
        elif keep_underscore and not keep_dash:
            s = re.sub(r"[^A-Za-z0-9\_ ]+", "", string.strip())
        else:
            s = re.sub(r"[^A-Za-z0-9 ]+", "", string.strip())
        if keep_caps:
            s = [x if is_all_caps(x) else x.lower() for x in s.split()]
        else:
            s = [x.lower() for x in s.split()]
        # logger.debug(f"string: {string}, s: {s}")
        return " ".join(s)
    # case: if already a number, return the number
    elif isinstance(string, (float, int)):
        return string
    else:
        return None


def recode_title_case(
    string: str,
    keep_dash: bool = False,
    keep_underscore: bool = False,
    keep_caps: bool = False,
) -> Union[str, None]:
    """Given a string, return the recoded string in title case (first letter of each word is capitalized) after dropping non-alphanumeric characters. Options:
    - keep_dash: keep '-' in string (default = False)
    - keep_underscore: keep '_' in string (default = False)
    - keep_caps: keep words in all caps in string (default = False).
    """
    string_ = recode_loweralphanumeric(string, keep_dash, keep_underscore, keep_caps)
    if string_ is None:
        return None
    elif isinstance(string_, str):
        s = [x.title() if not is_all_caps(x) else x for x in string_.split()]
        return " ".join(s)
    else:
        return None


def is_all_caps(string: str) -> bool:
    """Given a string, return True if all characters are uppercase, else return False"""
    if string is None:
        return False
    elif isinstance(string, str):
        string_ = string.strip()
        return string_.isupper()
    else:
        return False


def recode_list_loweralphanumeric(
    list_old: Union[List[str], Index],
    keep_dash: bool = False,
    keep_underscore: bool = False,
) -> Dict[str, str]:
    """Given a list of strings, keep only the alphanumeric parts of a string and any space (but not \n \t) and transforms all alpha into lowercase - removes all double and multiple spaces between words. Returns a dict of the old (key) and new string (value)"""
    if list_old is None:
        return None
    elif isinstance(list_old, list):
        return {
            x: recode_loweralphanumeric(
                x, keep_dash=keep_dash, keep_underscore=keep_underscore
            )
            for x in list_old
        }  # type: ignore
    elif isinstance(list_old, Index):
        return {
            x: recode_loweralphanumeric(
                x, keep_dash=keep_dash, keep_underscore=keep_underscore
            )
            for x in list(list_old)
        }  # type: ignore
    else:
        return None


def round_to_significant(x: "int|float", n: int = 3) -> Any:
    """rounds a number x to n significant figures, default = 3; if string that cannot be cast into number, returns the str. Returns all other types as is (including NaN)"""
    if isinstance(x, (int, float)) is False or x == 0:
        if x == 0:  # case x=0
            return 0
        elif isinstance(x, str):  # case x is a string that may contain a number
            try:  # case: is a number in string form
                x = float(x)
            except ValueError:  # case: not number in string form
                return x
        else:  # case: x is not a number or a string
            return x

    if isnan(x):
        return x
    else:
        return round(x, -int(floor(log10(abs(x)))) + (n - 1))


def camel_to_snake(camel_string):
    """converts a 'name' from camel case to snake case"""
    # Use regex to insert underscores before uppercase letters
    snake_string = re.sub(
        r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", camel_string
    )
    # split the string by "_", convert to lowercase, and join with "_"
    snake_string = "_".join([x.lower() for x in snake_string.split("_")])

    return snake_string

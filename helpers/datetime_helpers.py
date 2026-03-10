"""datetime helper functions"""

from typing import Union

from datetime import datetime, timedelta, date
from dateutil import parser

import pandas as pd

from config import logger


def get_age_in_years(this_date: Union[datetime, date, str]) -> int:
    """Get the age in years from a birth date with decimals for months and days. Returns negative number if date is in the future. Returns None if date is not a date or a string that can be converted to a date."""

    # cast candidate time to date
    if pd.isna(this_date):
        return None
    elif not isinstance(this_date, (date, datetime)):
        try:
            test_date = parser.parse(this_date).date()
        except TypeError as e:  # if it is already a date or datetime object
            logger.debug(f"Error parsing date: {e} for {this_date}")
            return None
    elif isinstance(this_date, datetime):
        test_date = this_date.date()
    else:
        test_date = this_date

    # logger.debug(f"test_date: {test_date}")

    today = date.today()
    age = timedelta(days=(today - test_date).days)
    years = age / timedelta(days=365.2425)
    return years

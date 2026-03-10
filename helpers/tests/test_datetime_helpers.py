# from django.test import TestCase
from pathlib import Path
import os
from datetime import date, datetime, timedelta

from helpers.datetime_helpers import get_age_in_years


# class TestFileHelpers(TestCase):
#     def setUp(self):
#         pass


def test_get_age_in_years():
    """test get_age_in_years"""
    today = date.today()
    test_data = [
        {"date": today - timedelta(days=365), "expected": 365 / 365.2425},
        {
            "date": today - timedelta(days=3 * 365 + 200),
            "expected": 3 + 200 / 365.2425,
        },
        {"date": today - timedelta(days=100), "expected": 100 / 365.2425},
        {"date": today + timedelta(days=100), "expected": -100 / 365.2425},
    ]
    # check that there are 3 files in list
    for data in test_data:
        assert round(get_age_in_years(data["date"]), 2) == round(data["expected"], 2)

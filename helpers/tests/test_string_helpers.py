from unittest import TestCase

from helpers.string_helpers import (
    recode_list_loweralphanumeric,
    recode_loweralphanumeric,
    round_to_significant,
    camel_to_snake,
    standardize_loweralphanumeric,
    standardize_regular_chars,
)

import pandas as pd


class TestStringHelpers(TestCase):
    def setUp(self):
        pass

    def test_recode_list_loweralphanumeric(self):
        test_data = [
            {
                "test_data": "Ronald  McDonald...",
                "expected": "ronald mcdonald",
            },
            {
                "test_data": " Ronald- McDonald",
                "expected": "ronald mcdonald",
            },
            {
                "test_data": "Ronald McDonald",
                "expected": "ronald mcdonald",
            },
            {
                "test_data": "Ronald GEE McDonald",
                "keep_caps": True,
                "expected": "ronald GEE mcdonald",
            },
            {
                "test_data": "ronald GEE McDonald",
                "expected": "ronald gee mcdonald",
            },
            {
                "test_data": "ronald G&E McDonald",
                "keep_caps": True,
                "expected": "ronald GE mcdonald",
            },
        ]
        for item in test_data:
            keep_caps = item.get("keep_caps", False)
            clean_name = recode_loweralphanumeric(
                item["test_data"], keep_caps=keep_caps
            )
            self.assertEqual(item["expected"], clean_name)

    def test_standardize_regular_chars(self):
        """test standardize_regular_chars"""
        result = standardize_regular_chars("(Csuite)-positions.!?%$ @=# [&;:] <>")
        self.assertEqual(result, "(Csuite)-positions.!?%$ @=# [&;:] <>")

    def test_recode_loweralphanumeric_number(self):
        """test that a number is returned as a number"""
        self.assertEqual(recode_loweralphanumeric(123), 123)
        self.assertEqual(recode_loweralphanumeric(123.0), 123.0)

    def test_recode_list_loweralphanumeric_pandas_index(self):
        df = pd.DataFrame({"Appled": [1, 2, 3], "Banana": [4, 5, 6]})
        recode_dict = recode_list_loweralphanumeric(df.columns)
        self.assertEqual(recode_dict, {"Appled": "appled", "Banana": "banana"})

    def test_round_to_significant(self):
        self.assertEqual(round_to_significant(0), 0)
        self.assertEqual(round_to_significant(123455), 123000)
        self.assertEqual(round_to_significant(0.0000123), 0.0000123)
        self.assertEqual(round_to_significant("0.123"), 0.123)
        self.assertEqual("abc", "abc")

    def test_camel_to_snake(self):
        self.assertEqual(camel_to_snake("camelCase"), "camel_case")
        self.assertEqual(camel_to_snake("CamelCase"), "camel_case")
        self.assertEqual(camel_to_snake("CamelCASE"), "camel_case")
        self.assertEqual(camel_to_snake("CamelCamelCamel"), "camel_camel_camel")
        self.assertEqual(camel_to_snake("2Camel2Camel2Camel"), "2_camel2_camel2_camel")

    def test_standardize_loweralphanumeric(self):
        """test standardize_loweralphanumeric"""
        test_data = [
            {
                "test_data": "Ronald 12 McDonald...",
                "expected": "ronald 12 mcdonald",
            },
            {
                "test_data": " Ronald---McDonald",
                "expected": "ronald mcdonald",
            },
            {
                "test_data": "Ronald McDonald.ronald",
                "expected": "ronald mcdonald ronald",
            },
            {
                "test_data": "ronald+GEE \n+ McDonald",
                "expected": "ronald gee mcdonald",
            },
        ]
        for item in test_data:
            clean_name = standardize_loweralphanumeric(item["test_data"])
            self.assertEqual(item["expected"], clean_name)

        # case: with alternate separator "-"
        test_data = [
            {
                "test_data": "Ronald 12 McDonald...",
                "expected": "ronald-12-mcdonald",
            },
            {
                "test_data": " Ronald---McDonald",
                "expected": "ronald-mcdonald",
            },
            {
                "test_data": "Ronald McDonald.ronald",
                "expected": "ronald-mcdonald-ronald",
            },
            {
                "test_data": "ronald+GEE \n+ McDonald",
                "expected": "ronald-gee-mcdonald",
            },
        ]
        for item in test_data:
            clean_name = standardize_loweralphanumeric(item["test_data"], "-")
            self.assertEqual(item["expected"], clean_name)

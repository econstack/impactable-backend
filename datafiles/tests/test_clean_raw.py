"""Test the clean_raw module"""

from pathlib import Path

from django.test import TestCase
import pandas as pd
from django.core.files.base import ContentFile

from config import DATA_BASE_DIR
from helpers.pandas_helpers import dataframe_info

from datafiles.helpers.clean_raw import clean_all_raw_files, clean_raw_file
from datafiles.models import Datafile, get_upload_path
from datafiles import logger


class TestCleanRaw(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        return

    def test_clean_raw_file(self):
        """test clean_raw_file"""
        # create a raw datafile instance
        # create a dataframe and save as csv
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
        file_path = Path(DATA_BASE_DIR, "temp", "test_raw_file.csv")
        csv_file = df.to_csv(index=False)
        # logger.debug(f"csv_file: {csv_file}")
        csv_file_as_bytes = ContentFile(
            csv_file.encode("utf-8")
        )  # Convert to byte content
        # logger.debug(f"csv_file_as_bytes: {csv_file_as_bytes}")

        test_filename = "test_raw_file.csv"
        self.raw_file = Datafile.objects.create(
            name=test_filename,
            file_type=Datafile.FileType.RAW,
        )
        self.raw_file.file.save(test_filename, csv_file_as_bytes)
        self.raw_file.save()
        # logger.debug(f"raw_file: {self.raw_file}")
        # logger.debug(f"raw_file.file: {self.raw_file.file}, {self.raw_file.file.name}")

        # check the raw file exists
        self.assertTrue(self.raw_file.file)
        self.assertEqual(self.raw_file.file_type, Datafile.FileType.RAW)

        # clean up the raw file
        cleaned_file = clean_raw_file(self.raw_file)

        # check the cleaned file exists
        self.assertTrue(cleaned_file)
        self.assertEqual(cleaned_file.file_type, Datafile.FileType.CLEANED)
        # logger.debug(
        #     f"file_type:{cleaned_file.file_type}, filename: {cleaned_file.original_filename}, path:{cleaned_file.file}"
        # )

        # check that it has the right path and is parquet file
        self.assertTrue(cleaned_file.file)
        self.assertTrue(cleaned_file.file.name.endswith(".parquet"))

        # check that it is linked to the raw file
        self.assertEqual(cleaned_file.raw_source, self.raw_file)

        # check it contains correct original filename
        self.assertTrue(test_filename in cleaned_file.original_filename)

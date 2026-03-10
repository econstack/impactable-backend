"""Test the models"""

from pprint import pformat
from pathlib import Path

from django.test import TestCase
import pandas as pd
from django.core.files.base import ContentFile

from helpers.file_helpers import read_csv
from config import DATA_BASE_DIR, MEDIA_BASE_DIR
from helpers.pandas_helpers import dataframe_info

from datafiles.helpers.clean_raw import clean_all_raw_files, clean_raw_file
from datafiles.models import Datafile, get_upload_path
from datafiles import logger


class TestDatafilesModel(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        return

    def setUp(self):
        pass

    def test_update_or_create(self):
        """Test the update_or_create method of the Datafile model"""
        # create a test dataframe
        df = pd.DataFrame(
            {
                "col1": [1, 2, 3],
                "col2": ["a", "b", "c"],
            }
        )

        # Create a new Datafile instance
        datafile, created = Datafile.objects.update_or_create(
            name="test_file",
            df=df,
            file_name="test_file.parquet",
            defaults={
                "description": "test description",
                "contact": "test contact",
                "file_type": Datafile.FileType.RAW,
            },
        )
        self.assertTrue(created)
        self.assertEqual(datafile.name, "test_file")
        self.assertEqual(datafile.description, "test description")
        self.assertEqual(datafile.contact, "test contact")
        self.assertEqual(datafile.file_type, Datafile.FileType.RAW)
        # load the file and see if it has the right data
        # read the file
        file_path = Path(MEDIA_BASE_DIR, str(datafile.file))
        df_loaded = pd.read_parquet(file_path)
        # check the dataframe
        self.assertTrue(df_loaded.equals(df))

        df["col3"] = df["col1"] * 2
        # Update the Datafile instance
        datafile, created = Datafile.objects.update_or_create(
            name="test_file",
            df=df,
            file_name="test_file2.parquet",
            defaults={
                "description": "updated description",
                "contact": "updated contact",
                "file_type": Datafile.FileType.CLEANED,
            },
        )
        self.assertFalse(created)
        # read the updated file
        file_path = Path(MEDIA_BASE_DIR, str(datafile.file))
        df_loaded = pd.read_parquet(file_path)
        # check the dataframe
        self.assertTrue(df_loaded.equals(df))

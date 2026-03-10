"""managemant command to make the test datafile table for datasets from current datafiles"""

from typing import List, Dict
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command

from datafiles import logger
from datafiles.helpers.files_io import read_datafile
from datafiles.helpers.load_table import make_save_test_datafile_table


class Command(BaseCommand):
    help = "make the test datafile table for datasets from current datafiles"

    def handle(self, *args, **kwargs):
        """make the test datafile table for datasets from current datafiles"""

        fp = make_save_test_datafile_table()

        logger.debug(f"Datafile table made and saved at:\n{fp}")

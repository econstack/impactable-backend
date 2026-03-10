"""managemant command to delete unused datafile files in the datafiles folder"""

from typing import List, Dict
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command

from datafiles import logger
from datafiles.helpers.delete_unused import delete_unused_datafiles
from datafiles.helpers.load_table import make_save_test_datafile_table


class Command(BaseCommand):
    help = "delete unused datafile files in the datafiles folder"

    def handle(self, *args, **kwargs):
        """delete unused datafile files in the datafiles folder"""

        res = delete_unused_datafiles()
        unused = res["unused_files_removed"]

        logger.debug(
            f"Removed {len(unused)} unused datafiles from the datafiles folder."
        )

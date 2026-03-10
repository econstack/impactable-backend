from django.core.management.base import BaseCommand

from datafiles.helpers.clean_raw import clean_all_raw_files


class Command(BaseCommand):
    help = "Clean up all raw files that have not been cleaned yet. Returns list of cleaned datafiles."

    def handle(self, *args, **kwargs):
        """see help message for more info"""

        # clean all raw files
        cleaned_datafiles = clean_all_raw_files()
        # print the cleaned datafiles
        for cleaned_datafile in cleaned_datafiles:
            self.stdout.write(
                self.style.SUCCESS(f"Cleaned datafile: {cleaned_datafile}")
            )

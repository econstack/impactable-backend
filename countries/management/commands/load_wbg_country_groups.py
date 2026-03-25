from django.core.management.base import BaseCommand
from pathlib import Path
import pandas as pd
from typing import Union

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from config import DATA_BASE_DIR, logger
from countries.models import Country, CountryGroup


class Command(BaseCommand):
    help = "Load WBG country groups into the CountryGroup model"

    def handle(self, *args, **options):
        filepath = Path(DATA_BASE_DIR, "countries", "wbg_country_groups.csv")
        load_wbg_country_groups(filepath)
        self.stdout.write(self.style.SUCCESS("Country groups loaded successfully"))


def load_wbg_country_groups(filepath: Path):
    """
    Loads the WBG country groups into the database. Given a filepath to a CSV file with columns for iso3 ('CountryCode') and for the wbg group code ('GroupCode'), populates/updates the country group table and, where needed, adds to the country table.
    """
    # read in file to pandas
    df = pd.read_csv(filepath)

    # create country groups
    df_groups = df[["GroupCode", "GroupName"]].drop_duplicates().copy()
    df_groups["id"] = df_groups.apply(create_country_groups, axis=1)
    logger.debug(f"created {len(df_groups)} country groups")

    # assign countries to country groups
    df["cgroup_pk"] = df.apply(save_row_country_group, axis=1)

    return


def create_country_groups(row: pd.Series) -> int:
    """create or update country group and return id of the group given row/series with group code and group name"""
    group_code = row.get("GroupCode")
    group_name = row.get("GroupName")
    cgroup, created = CountryGroup.objects.update_or_create(name=group_name)
    return cgroup.pk


def save_row_country_group(row: pd.Series) -> Union[None, int]:
    """assign country to country group given row with "country code" which should be its iso3 code, and group code. Will add the country group if the country group (based on group code) does not exist. Expects the country to already exist in the country table."""

    group_name = row.get("GroupName")
    country_code = row.get("CountryCode")

    country_group, _ = CountryGroup.objects.get_or_create(name=group_name)

    try:
        country = Country.objects.get(iso3=country_code)
    except (ObjectDoesNotExist, IntegrityError) as err:
        logger.debug(
            f"Error: {err}. \n Cannot add country with iso3: {country_code}, to country group: {group_name}"
        )
        return None

    country_group.countries.add(country)
    country_group.save()

    return country_group.pk

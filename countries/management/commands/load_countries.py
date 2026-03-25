import json
from django.core.management.base import BaseCommand
from countries.models import Country
from pathlib import Path

from config import DATA_BASE_DIR


class Command(BaseCommand):
    help = "Load countries from JSON into the Country model"

    def handle(self, *args, **options):
        json_path = Path(DATA_BASE_DIR, "countries", "countries.json")

        with open(json_path, "r") as f:
            countries = json.load(f)

        for entry in countries:
            Country.objects.update_or_create(
                iso3=entry["iso3"],
                defaults={"name": entry["name"]},
            )

        self.stdout.write(self.style.SUCCESS("Countries loaded successfully"))

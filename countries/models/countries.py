from django.db import models

from organization.models import Organization


# Create your models here.
class Country(models.Model):
    iso3 = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class CountryGroup(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="Null = global group type (e.g. World Bank)",
    )
    countries = models.ManyToManyField(Country, related_name="groups")

    class Meta:
        unique_together = ("name", "organization")

    def __str__(self):
        return (
            f"{self.name} ({self.organization.name if self.organization else 'Global'})"
        )

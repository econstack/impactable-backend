from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class IndicatorConfig(models.Model):
    """generic base impact indicator.
    - name (full name of the indicator)
    - short_name (short name of the indicator)
    - code (optonal code for the indicator)
    - unit_scale (unit scale of the indicator - number, ratio, percentage, etc.)
    - unit_type (unit type of the indicator - kwh, km, etc.)
    - desc (description of the indicator)
    - comments (comments on the indicator), including how this indicator is calculated or constructed from other indicators
    - is_categorical (is the indicator categorical (or continuous) (boolean)
    - categorical_values (if categorical, the values the indicator can take) (string of values separated by semi-colon ';' ) #TODO: implement validation for this field when parsing data
    - is_derived (is the indicator derived from other indicators (boolean)
    - derived_notes (notes on how the indicator is derived from other indicators)
    - source_indicators (foreign key to other indicators that are the source of this indicator) (many-to-many)
    """

    class UnitScale(models.TextChoices):
        NUM = "Number", "Number"
        RATIO = "Ratio", "Ratio"  # share usually in range 0-1
        PCT = (
            "Percentage",
            "Percentage",
        )  # range usually 0-100 but can be negative and > 100
        K = "Thousands", "Thousands"
        M = "Millions", "Millions"
        B = "Billions", "Billions"
        OTHER = "Other", "Other"
        CAT = "Categorical", "Categorical"
        TF = "True/False", "True/False"

    # original name from data source
    name = models.CharField(max_length=200, unique=True)
    # standardized name of the indicator
    standard_name = models.CharField(max_length=200, blank=True, null=True)
    # variant of the indicator (e.g. annual pct change, difference from baseline, etc.) and should be combined with short_name to make a unique identifier (e.g. GDP per capita, annual pct change)
    variant = models.CharField(max_length=200, blank=True, null=True)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    # optional code for indicator
    code = models.CharField(max_length=50, blank=True, null=True)
    # scale of the indicator (e.g. number, ratio, millions, etc.)
    unit_scale = models.CharField(
        max_length=20, choices=UnitScale.choices, default=UnitScale.NUM
    )
    # measure unit of the indicator (e.g. USD per capita, kwh, km, etc.)
    unit_type = models.CharField(max_length=50, blank=True, null=True)
    # description of the indicator and any other comments on the indicator (e.g. measurement issues, etc.)
    desc = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    # is_categorical is True if the indicator is categorical and can take on a limited number of values, List of values separated by semi-colon ';' in categorical_values
    # todo: implement get/set for categorical_values
    is_categorical = models.BooleanField(default=False)
    # todo: implement as csv string of values, can be parsed into list when needed, and implement validation to ensure that if is_categorical is True, then categorical_values is not null and has at least one value, and if is_categorical is False, then categorical_values should be null
    categorical_values = models.TextField(blank=True, null=True)

    # is_derived is True if the indicator is derived from other indicators with notes on derivation in derived_notes
    is_derived = models.BooleanField(default=False)
    derived_notes = models.TextField(blank=True, null=True)
    source_indicators = models.ManyToManyField("self", blank=True)

    # guidance notes on measurement or usage
    guidance = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name[:40]

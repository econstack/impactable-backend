"""Custom admin classes for Django admin"""

from django.contrib import admin
from helpers.string_helpers import round_to_significant

from config import logger


class BaseAdmin(admin.ModelAdmin):
    """Handles column formatting in list display for numbers. Usage: Inherit from this class and define list_display as a list of strings or tuples. If a tuple, the first element is the field name and the second element is the number of significant figures to round to."""

    def __init__(self, *args, **kwargs):
        def generate_formatter(name, ndigits: int = 3):
            formatter = lambda o: round_to_significant(getattr(o, name) or 0, ndigits)
            formatter.short_description = name
            formatter.admin_order_field = name
            return formatter

        all_fields = []
        for f in self.list_display:
            if isinstance(f, str):
                all_fields.append(f)
            else:
                new_field_name = f[0] + "_formatted"
                setattr(self, new_field_name, generate_formatter(f[0], f[1]))
                all_fields.append(new_field_name)
        self.list_display = all_fields

        super().__init__(*args, **kwargs)

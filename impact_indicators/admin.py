from django.contrib import admin

# Register your models here.
from .models.IndicatorConfig import IndicatorConfig


@admin.register(IndicatorConfig)
class IndicatorConfigAdmin(admin.ModelAdmin):
    # list view
    list_display = ("name", "short_name")
    search_fields = [
        "name",
    ]

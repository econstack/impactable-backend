from django.contrib import admin

from .models import Country, CountryGroup


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "iso3")
    search_fields = ["name", "iso3"]


@admin.register(CountryGroup)
class CountryGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "organization")
    search_fields = ["name", "organization__name"]
    list_filter = ["organization"]

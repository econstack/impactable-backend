from django.contrib import admin

from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    # list view
    list_display = ("name", "slug")
    search_fields = [
        "name",
    ]

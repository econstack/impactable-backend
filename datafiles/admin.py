from django.contrib import admin

# Register your models here.
from .models import Datafile


@admin.register(Datafile)
class DatafileAdmin(admin.ModelAdmin):
    # list view
    list_display = ("name", "file_type", "created_at")
    search_fields = [
        "name",
    ]
    list_filter = [
        "file_type",
    ]

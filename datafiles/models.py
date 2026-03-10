import os
from pathlib import Path
from pprint import pformat

from django.db import models
from django.core.files.base import ContentFile
import pandas as pd

from uuid import uuid4

from config import MEDIA_BASE_DIR
from datafiles import logger


def get_upload_path(instance, filename):
    # Get the file extension
    ext = filename.split(".")[-1]
    # Create a new file name, e.g., based on the model instance
    uuid = uuid4()
    # logger.debug(f"uuid: {uuid}")
    # logger.debug(f"filename: {filename}")

    # Create a new file name, e.g., based on the model instance
    new_filename = f"{'.'.join(filename.split('.')[:-1])}_{uuid}.{ext}"
    # Return the custom file path
    return os.path.join("uploads/datafiles/", new_filename)


class DatafileManager(models.Manager):
    """custom manager for datafile model"""

    def update_or_create(self, defaults=None, **kwargs):
        """override the update_or_create method to save the dataframe as a parquet and save the previous file path"""
        # logger.debug(f"update_or_create, kwargs.keys(): \n{pformat(kwargs.keys())}")
        # logger.debug(f"defaults: {defaults}")
        defaults = defaults or {}

        # logger.debug(f"update_or_create: \n{pformat(kwargs)}")
        # get the dataframe and save it as a parquet file, if missing, then raise error
        df = kwargs.pop("df", None)
        # logger.debug(f"df: {df}")
        if df is None:
            raise ValueError("Dataframe is required to save the file")

        # check for valid file_name
        file_name = kwargs.pop("file_name", None)
        # logger.debug(f"file_name: {file_name}")
        if pd.isna(file_name):
            logger.warning(
                f"File name is required to save the file. Invalid file name provided: {file_name}. Please provide a valid file name ending with .parquet"
            )

        else:
            pass

        # save the dataframe as a parquet file
        fp = get_upload_path(None, f"{file_name}")
        # get the full file path for saving cleaned file
        fp_ = Path(MEDIA_BASE_DIR, fp)
        # save the dataframe to a datafile
        parquet_file = df.to_parquet()
        parquet_file_as_bytes = ContentFile(parquet_file)

        obj, created = super().update_or_create(defaults=defaults, **kwargs)
        obj.file.save(file_name, parquet_file_as_bytes)

        return obj, created


class Datafile(models.Model):
    """datafile model for datafile management"""

    class FileType(models.TextChoices):
        RAW = "raw"
        CLEANED = "cleaned"
        ETL = "etl"
        OTHER = "other"
        TABLEAU = "tableau"

    name = models.CharField(max_length=255, help_text="name of the datafile, required")
    contact = models.CharField(
        max_length=255,
        blank=True,
        help_text="email or name of contact person who provided datafile",
    )  # email or name of contact person who provided datafile
    description = models.TextField(blank=True, help_text="description of the datafile")
    notes = models.TextField(blank=True)
    file_type = models.CharField(
        max_length=50, choices=FileType.choices, default=FileType.OTHER
    )
    original_filename = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to=get_upload_path)
    previous_file_path = models.FileField(
        upload_to=get_upload_path, blank=True, null=True
    )  # previous version of the file
    created_at = models.DateTimeField(auto_now_add=True)

    # for excel sheets
    sheet_name = models.CharField(max_length=255, blank=True)
    header_row = models.IntegerField(default=0)

    # for cleaned files
    raw_source = models.ForeignKey(
        "self",  # Points to the same model
        on_delete=models.SET_NULL,  # You can choose SET_NULL, CASCADE, or PROTECT
        null=True,  # Allows this field to be null
        blank=True,  # Field can remain empty
        related_name="cleaned",  # Optional: helpful for reverse relationships
    )

    objects = DatafileManager()

    def save(self, *args, **kwargs):
        """override the save method to save the previous file path and orginal filename"""
        # logger.debug(f"self.file: {self.file}")
        # Save the original filename
        if self.file and not self.original_filename:
            original_file_name = self.file.name.split("/")[-1]
            self.original_filename = original_file_name

        # save the previous file
        if self.pk:
            old_instance = Datafile.objects.get(pk=self.pk)
            if (
                old_instance.file
                and old_instance.file != self.file
                and old_instance.file_type == self.file_type
            ):
                # Store the old file path in the 'previous_file_path' field
                self.previous_file_path = old_instance.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

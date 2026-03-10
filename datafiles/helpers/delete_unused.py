"""clean up folders for unused datafiles that are not in use anymore"""

from typing import Dict, List
from pathlib import Path
from django.db.models.fields.files import FieldFile

from core import MEDIA_BASE_DIR

from datafiles import logger
from datafiles.models import Datafile


def delete_unused_datafiles() -> Dict[str, List[str]]:
    """delete unused files in the datafiles folder (i.e. all files which are not in current file or previous file path for datafile.) Returns a dict with the following keys:
    - unused_files_removed: list of files that were removed
    - used_files: list of files that are in use
    """
    # get all files in the datafiles folder
    datafiles_folder = Path(MEDIA_BASE_DIR, "uploads/datafiles/")
    # get all files in the datafiles folder
    all_files = [f for f in datafiles_folder.glob("**/*") if f.is_file()]

    # get all files that are not in use
    used_files = set()
    for obj in Datafile.objects.all():
        used_files.add(obj.file.path)
        used_files.add(obj.previous_file_path)
    # get all the filenames from the used files
    used_files = list(used_files)
    used_filenames = []
    for file in used_files:
        if isinstance(file, Path):
            used_filenames.append(file.name)
        elif isinstance(file, FieldFile):
            used_filenames.append(file.name.split("/")[-1])
        elif isinstance(file, str):
            used_filenames.append(file.split("/")[-1])
        else:
            logger.warning(f"unknown file type: {file}, {type(file)}")

    # list files that are not in use
    unused_files = [f for f in all_files if f.name not in used_filenames]
    # logger.debug(f"unused files: {unused_files}")

    # delete all files that are not in use
    for file in unused_files:
        file.unlink()

    return {"unused_files_removed": unused_files, "used_files": used_files}  # type: ignore

import logging
from .custom_logger import CustomLogger, LOG_LEVEL_GLOBAL
from pathlib import Path

local_log_level = logging.DEBUG
log_level = LOG_LEVEL_GLOBAL or local_log_level
# print(f"config default log level:{log_level}")

# set default logger for app (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logger = CustomLogger.getLogger(name="config", level=local_log_level)
PROJECT_BASE_DIR = Path(__file__).parent.parent
DATA_BASE_DIR = Path(PROJECT_BASE_DIR, "datasets")
MEDIA_BASE_DIR = Path(PROJECT_BASE_DIR, "media")

from config.custom_logger import CustomLogger, LOG_LEVEL_GLOBAL
import logging
from pathlib import Path

# set local default log level
local_log_level = logging.DEBUG
log_level = LOG_LEVEL_GLOBAL or local_log_level
logger = CustomLogger.getLogger(name="datafiles", level=local_log_level)

# set app dir
APP_BASE_DIR = Path(__file__).parent

import json
import logging.config
import os
import time

""" Define directories and files """
ROOT_DIR = os.getcwd()
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
CONFIGS_DIR = os.path.join(ROOT_DIR, "configs")
API_CONFIG = os.path.join(CONFIGS_DIR, "api_config.json")

""" Set up logger directory and format """
os.makedirs(LOGS_DIR, exist_ok=True)

log_name = time.strftime("%m%d%Y-%H:%M:%S")

logging.disable(logging.DEBUG)
logging.config.fileConfig(
    fname=os.path.join(CONFIGS_DIR, "logger.conf"),
    disable_existing_loggers=False,
    defaults={"logfilename": f"{LOGS_DIR}/{log_name}.log"},
)
logger = logging.getLogger(__name__)

""" Load configuration values"""
with open(API_CONFIG, "r") as config_file:
    config = json.load(config_file)

api_config = config

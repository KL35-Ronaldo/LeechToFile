import os
import time
import logging

if bool(os.environ.get("ENV", False)):
    from tobrot.sample_config import Config
else:
    from tobrot.config import Config

from logging.handlers import RotatingFileHandler

TG_BOT_TOKEN = Config.TG_BOT_TOKEN
APP_ID = Config.APP_ID
API_HASH = Config.API_HASH
OWNER_ID = Config.OWNER_ID
AUTH_CHANNEL = list(Config.AUTH_CHANNEL)
AUTH_CHANNEL.append(OWNER_ID)
AUTH_CHANNEL = list(set(AUTH_CHANNEL))
DOWNLOAD_LOCATION = Config.DOWNLOAD_LOCATION
MAX_FILE_SIZE = Config.MAX_FILE_SIZE
TG_MAX_FILE_SIZE = Config.TG_MAX_FILE_SIZE
FREE_USER_MAX_FILE_SIZE = Config.FREE_USER_MAX_FILE_SIZE
CHUNK_SIZE = Config.CHUNK_SIZE
DEF_THUMB_NAIL_VID_S = Config.DEF_THUMB_NAIL_VID_S
MAX_MESSAGE_LENGTH = Config.MAX_MESSAGE_LENGTH
PROCESS_MAX_TIMEOUT = Config.PROCESS_MAX_TIMEOUT
ARIA_TWO_STARTED_PORT = Config.ARIA_TWO_STARTED_PORT
EDIT_SLEEP_TIME_OUT = Config.EDIT_SLEEP_TIME_OUT
MAX_TIME_TO_WAIT_FOR_TORRENTS_TO_START = Config.MAX_TIME_TO_WAIT_FOR_TORRENTS_TO_START
MAX_TG_SPLIT_FILE_SIZE = Config.MAX_TG_SPLIT_FILE_SIZE
FINISHED_PROGRESS_STR = Config.FINISHED_PROGRESS_STR
UN_FINISHED_PROGRESS_STR = Config.UN_FINISHED_PROGRESS_STR
TG_OFFENSIVE_API = Config.TG_OFFENSIVE_API
CUSTOM_FILE_NAME = Config.CUSTOM_FILE_NAME
LEECH_COMMAND = Config.LEECH_COMMAND
YTDL_COMMAND = Config.YTDL_COMMAND
RCLONE_CONFIG = Config.RCLONE_CONFIG
DESTINATION_FOLDER = Config.DESTINATION_FOLDER
INDEX_LINK = Config.INDEX_LINK
CANCEL_COMMAND_G = Config.CANCEL_COMMAND_G
GET_SIZE_G = Config.GET_SIZE_G
STATUS_COMMAND = Config.STATUS_COMMAND
SAVE_THUMBNAIL = Config.SAVE_THUMBNAIL
CLEAR_THUMBNAIL = Config.CLEAR_THUMBNAIL
CLEAR_UNDELETED = Config.CLEAR_UNDELETED
PYTDL_COMMAND = Config.PYTDL_COMMAND
BOT_START_TIME = time.time()
LOG_COMMAND = Config.LOG_COMMAND

if os.path.exists("leecher.txt"):
	with open("leecher.txt", "r+") as f_d:
		f_d.truncate(0)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            "leecher.txt",
            maxBytes=FREE_USER_MAX_FILE_SIZE,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__) 

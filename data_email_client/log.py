import getpass
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import socket


logfile_name = "data_email_client.log"
try:
    username = getpass.getuser()
    home_dir = Path(os.path.expanduser("~/"))
    log_dir = home_dir / ".data_email_client"
    log_dir.mkdir(exist_ok=True)
    logfile = log_dir / logfile_name
except Exception:
    logfile = Path(logfile_name)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

f_handler = RotatingFileHandler(logfile, maxBytes=1024 * 10000, backupCount=4)
c_handler = logging.StreamHandler()

f_handler.setLevel(logging.DEBUG)
c_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | [%(module)s:%(lineno)d] | %(message)s"
)

f_handler.setFormatter(formatter)
c_handler.setFormatter(formatter)

log.addHandler(f_handler)
log.addHandler(c_handler)


import logging
import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.remote_connection import LOGGER

LOGGER.setLevel(logging.WARNING)

from ecb import ECB

# PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
# DRIVER_BIN = os.path.join(PROJECT_ROOT, "/opt/homebrew/Caskroom/chromedriver/118.0.5993.70/chromedriver-mac-arm64/chromedriver")
#
# service = Service(executable_path=DRIVER_BIN)

service = Service(executable_path=r"F:\firefoxdriver\geckodriver.exe")

formatter = logging.Formatter('%(name)s: [%(levelname)s] [%(asctime)s] %(message)s')
current_date = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
driver = webdriver.Firefox(service=service)
# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(formatter)
# stream_handler.setLevel(logging.DEBUG)
# logger.addHandler(stream_handler)

parser = ECB(driver)
docs = parser.content()

print(*docs, sep='\n\r\n')

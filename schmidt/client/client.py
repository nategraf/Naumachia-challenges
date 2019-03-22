import logging
import os
import random
import requests
import time

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
WEB_URL = os.environ.get("WEB_URL", "http://localhost:8080")
USERNAME = os.environ.get("USERNAME", "alice")
PASSWORD = os.environ.get("PASSWORD", "password")

delay_mu = 10.0
delay_sigma = 2.0
http_timeout = 10

logging.basicConfig(format="[%(levelname)7s %(asctime)s %(name)s] %(message)s", datefmt="%m-%d %H:%M:%S")
logger = logging.getLogger('client')
logger.setLevel(LOG_LEVEL)

def delay():
    length = abs(random.gauss(delay_mu, delay_sigma))
    logger.info("Sleeping for %.2f seconds", length)
    time.sleep(length)

if __name__ == "__main__":
    while True:
        delay()
        try:
            logger.info("GET {}".format(WEB_URL))
            resp = requests.get(WEB_URL, auth=(USERNAME, PASSWORD))
            logger.info(str(resp))

        except OSError as err:
            logger.exception("encountered error in main loop")
            continue

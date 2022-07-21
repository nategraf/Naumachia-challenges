import logging
import os
import random
import requests
import time

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
WEB_URL = os.environ.get("WEB_URL", "http://localhost:8080")
USERNAME = os.environ.get("USERNAME", "alice")
PASSWORD = os.environ.get("PASSWORD", "password")
NAMESERVER_IP = os.environ.get("NAMESERVER_IP", "172.30.0.2")

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

# Overwrite the resolve.conf file with the IP of the NS server
def configure_resolve_conf():
    with open('/etc/resolv.conf', 'w') as conf:
        conf.write(f"nameserver {NAMESERVER_IP}")

if __name__ == "__main__":
    # Upon first launching, override the resolv.conf file that Docker mounts.
    configure_resolve_conf()

    while True:
        delay()
        try:
            logger.info("GET {}".format(WEB_URL))
            resp = requests.get(WEB_URL, auth=(USERNAME, PASSWORD))
            logger.info(str(resp))

        except OSError as err:
            logger.exception("encountered error in main loop")
            continue

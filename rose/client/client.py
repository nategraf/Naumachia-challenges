from time import sleep
from lxml import etree
from os import path, environ, makedirs
from dns.resolver import NoAnswer as DnsNoAnswer, NXDOMAIN
from dns.exception import Timeout as DnsTimeout
from PySide2.QtWebKitWidgets import QWebSettings
from urllib.parse import urlencode, urljoin
from ghost import Ghost
import dns.resolver
import io
import random
import sys
import logging
import shutil
import itertools

LOG_LEVEL = environ.get('LOG_LEVEL', 'INFO')
WEBKIT_CACHE = environ.get('WEBKIT_CACHE', '/tmp/webcache')
ROSE_USER = environ.get("ROSE_USER", None) or environ["ADMIN_USER"]
ROSE_PASS = environ.get("ROSE_PASS", None) or environ["ADMIN_PASS"]
HTTP_URL = environ["HTTP_URL"]
NAMESERVER = environ["NAMESERVER"]

delay_mu = 4
delay_sigma = 2
iteration_mu = 15
iteration_sigma = 8
retry_delay = 5

_levelnum = getattr(logging, LOG_LEVEL.upper(), None)
if not isinstance(_levelnum, int):
    raise ValueError('Invalid log level: {}'.format(LOG_LEVEL))

logging.basicConfig(level=_levelnum, format="[%(levelname)s %(asctime)s] %(message)s", datefmt="%m-%d %H:%M:%S")
logger = logging.getLogger('httpclient')

def delay():
    length = abs(random.gauss(delay_mu, delay_sigma))
    logger.debug("Sleeping for %0.2f seconds", length)
    sleep(length)

def init_dns():
    resolver = dns.resolver.Resolver()
    answers = resolver.query(NAMESERVER, "A")

    with open('/etc/resolv.conf', 'r') as conf:
        conf_lines = [line.strip() for line in conf if line.strip()]

    # Add it as the primary name server
    for ans in answers:
        conf_lines.insert(0, "nameserver {0}\n".format(ans))

    with open('/etc/resolv.conf', 'w') as conf:
        for line in conf_lines:
            conf.write("{0}\n".format(line))

def configure_caching():
    """Remove any existing cache and setup the correct settings"""
    if WEBKIT_CACHE:
        # Reset the cache folder
        if path.exists(WEBKIT_CACHE):
            shutil.rmtree(WEBKIT_CACHE)
        makedirs(WEBKIT_CACHE)

        # Ghost disables caching globally at the start of each session
        # http://doc.qt.io/archives/qt-5.5/qwebsettings.html#enablePersistentStorage
        QWebSettings.setMaximumPagesInCache(100)
        QWebSettings.setObjectCacheCapacities(4 * 1024 * 1024, 8 * 1024 * 1024, 12 * 1024 * 1024)
        QWebSettings.enablePersistentStorage(WEBKIT_CACHE)

class ClientError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class MarkovNode:
    def __init__(self, value):
        self.value = value
        self.adjacencies = []

    def add(self, node, weight):
        self.adjacencies.append((node, weight))

    def __iter__(self):
        curr = self
        while curr and curr.adjacencies:
            yield curr

            # Weighted selection of the next node
            nodes, weights = zip(*curr.adjacencies)
            selector = random.uniform(0, sum(weights))
            for node, weight in zip(nodes, itertools.accumulate(weights)):
                if selector <= weight:
                    curr = node
                    break

class GetRequest:
    def __init__(self, page, precondition=None):
        self.address = urljoin(HTTP_URL, page)
        self.precondition = precondition

    def ghostargs(self):
        return {'address': self.address}

    def __str__(self):
        return "HTTP GET {}".format(self.address)

class PostRequest:
    def __init__(self, page, data, precondition=None):
        self.address = urljoin(HTTP_URL, page)
        self.data = data
        self.precondition = precondition

    def ghostargs(self):
        body = urlencode(self.data)
        return {
            'address': self.address,
            'method': 'POST',
            'headers': {
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": str(len(body))
            },
            'body': body
        }

    def __str__(self):
        return "HTTP POST {} {}".format(self.address, self.data)

def build_markov_model():
    # Create all the Markov chain nodes
    root = MarkovNode(GetRequest('/'))
    negozio = MarkovNode(GetRequest('/negozio', lambda s: s.exists('a[href="/negozio"]')))
    info = MarkovNode(GetRequest('/informazioni', lambda s: s.exists('a[href="/informazioni"]')))
    home = MarkovNode(GetRequest('/home', lambda s: s.exists('a[href="/home"]')))
    accedi_get = MarkovNode(GetRequest('/accedi', lambda s: s.exists('a[href="/accedi"]')))
    accedi_post = MarkovNode(PostRequest('/accedi', {'user': ROSE_USER, 'password': ROSE_PASS}, lambda s: s.exists('input[name="user"]') and s.exists('input[name="password"]')))
    negozio_authed = MarkovNode(GetRequest('/negozio', lambda s: s.exists('a[href="/negozio"]')))
    esci = MarkovNode(GetRequest('/esci', lambda s: s.exists('a[href="/esci"]')))

    # Link the markov chain
    root.add(negozio, 0.4)
    root.add(info, 0.6)

    negozio.add(info, 0.3)
    negozio.add(home, 0.1)
    negozio.add(accedi_get, 0.6)

    info.add(negozio, 0.7)
    info.add(accedi_get, 0.2)
    info.add(home, 0.1)

    home.add(accedi_get, 0.5)
    home.add(negozio, 0.25)
    home.add(info, 0.25)

    accedi_get.add(accedi_post, 1)
    accedi_post.add(negozio_authed, 1)

    negozio_authed.add(negozio_authed, 0.2)
    negozio_authed.add(esci, 0.8)

    # Esci should be the last
    esci.add(None, 1)

    return root
if __name__ == "__main__":
    # Configure DNS
    attempt = 0
    while True:
        attempt = attempt + 1
        try:
            logger.info("Initializing nameserver settings...")
            init_dns()
        except(DnsTimeout, DnsNoAnswer, NXDOMAIN) as err:
            logger.error("Initializing nameserver settings: FAILED %s", err)
            if attempt > 3:
                raise
        else:
            logger.info("Initializing nameserver settings: SUCCESS")
            break
        sleep(retry_delay)

    g = Ghost()
    model = build_markov_model()

    while True:
        length = abs(random.gauss(iteration_mu, iteration_sigma))
        logger.info("Sleeping %0.2f seconds before the next iteration", length)
        sleep(length)

        with g.start(javascript_enabled=False) as session:
            session.logger.setLevel(logging.WARNING)
            configure_caching()
            try:
                for node in model:
                    req = node.value
                    if req.precondition and not req.precondition(session):
                        raise ClientError("Precondition failed for {}".format(req))

                    logger.info("%s", req)
                    page, _ = session.open(**req.ghostargs())

                    if not page:
                        raise ClientError("Ghost didn't return a page")
                    if page.http_status >= 400:
                        raise ClientError("Received HTTP error code {}".format(page.http_status))

                    delay()

            except Exception as err:
                logger.error("Exception: %s", err)
                continue

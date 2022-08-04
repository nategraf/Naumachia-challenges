from time import sleep
from lxml import etree
from os import path, environ
from OpenSSL import crypto, SSL
from naumhttpadapter import NaumHTTPAdapter, VerificationError
import requests
import random
import urllib3
import sys
import io

script_dir = path.dirname(__file__)

_print = print
def print(*args, **kwargs):
    _print(*args, **kwargs)
    sys.stdout.flush()

cacert = environ.get("CA_PATH", "/etc/ssl/ca.naum.crt")
url = environ.get("CATFACTS_URL", "https://catfacts.naum")
quiet = environ.get("CLIENT_QUIET", False)
user = environ.get("CATFACTS_USER")
passwd = environ.get("CATFACTS_PASS")

delay_mean = 2
delay_var = 0.6
iteration_delay = 10
retry_delay = 5
http_timeout = 10

def delay():
    length = abs(random.gauss(delay_mean, delay_var))
    sleep(length)

if __name__ == "__main__":
    while True:
        print("Sleeping before begining an iteration")
        sleep(iteration_delay)

        with requests.Session() as sess:
            try:
                urllib3.disable_warnings()
                sess.mount('https:', NaumHTTPAdapter())
                sess.verify = cacert

                last_resp = None
                tree = None

                for i in range(3):
                    print("GET {}".format(url))
                    last_resp = sess.get(url, timeout=http_timeout)

                    if not quiet:
                        tree = etree.parse(io.StringIO(last_resp.text), etree.HTMLParser())
                        fact = tree.xpath('//p[@class="lead"]')[0].text
                        print("Got a fact! '{}'".format(fact))

                    delay()

                if not tree:
                    tree = etree.parse(io.StringIO(last_resp.text), etree.HTMLParser())

                # If there is a CRSF token, include it in the form.
                try:
                    csrf_token = tree.xpath('//form[@action="/login"]/input[@name="csrf_token"]')[0].get('value')
                    creds = {
                        "user": user,
                        "passwd": passwd,
                        "csrf_token": csrf_token
                    }
                except Exception as err:
                    print("Got error trying to get CSRF token", err)
                    creds = {
                        "user": user,
                        "passwd": passwd,
                    }

                print("POST {}".format("{}/login".format(url)))
                sess.post(url="{}/login".format(url), data=creds, timeout=http_timeout).raise_for_status()
                delay()

                print("GET {}".format(url))
                last_resp = sess.get(url, timeout=http_timeout)

                if not quiet:
                    tree = etree.parse(io.StringIO(last_resp.text), etree.HTMLParser())
                    fact = tree.xpath('//p[@class="lead"]')[0].text
                    print("Bonus Fact (flag)! '{}'".format(fact))

            except (requests.exceptions.ConnectionError, VerificationError) as err:
                print("Error: " + str(err))
                continue

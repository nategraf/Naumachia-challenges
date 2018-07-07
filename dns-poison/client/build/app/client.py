import io
import requests
import random
import urllib3
import sys
import dns.resolver
from dns.resolver import NoAnswer as DnsNoAnswer, NXDOMAIN
from dns.exception import Timeout as DnsTimeout
from time import sleep
from lxml import etree
from os import path, environ

script_dir = path.dirname(__file__)

_print = print
def print(*args, **kwargs):
    _print(*args, **kwargs)
    sys.stdout.flush()

cacert = environ.get("CERT_PATH", "/certs/catfacts.naum.cert")
nameserver = environ.get("CLIENT_NAMESERVER", "ns.docker")
quiet = environ.get("CLIENT_QUIET", False)
url = environ.get("CATFACTS_URL", "http://catfacts.naum")
user = environ.get("CATFACTS_USER", "catdaddy")
passwd = environ.get("CATFACTS_PASS", "fxVVC8GQNTvUbeJn")

delay_mean = 2
delay_var = 0.6
iteration_delay = 10
retry_delay = 5

def delay():
    length = abs(random.gauss(delay_mean, delay_var))
    sleep(length)

def init_dns():
    resolver = dns.resolver.Resolver()
    answers = resolver.query(nameserver, "A")
    
    with open('/etc/resolv.conf', 'a') as conf:
        for ans in answers:
            conf.write("nameserver {0}\n".format(ans))


if __name__ == "__main__":
    attempt = 0
    while True:
        attempt = attempt + 1
        try:
            print("Initializing nameserver settings:", end=" ")
            init_dns()
        except(DnsTimeout, DnsNoAnswer, NXDOMAIN) as err:
            print("FAILED {}".format(err))
            if attempt > 3:
                raise
        else:
            print("SUCCESS")
            break
        sleep(retry_delay)

    while True:
        sleep(iteration_delay)

        with requests.Session() as sess:
            try:
                urllib3.disable_warnings()

# No verification to make this problem a little easier
#                sess.verify = cacert
                
                last_resp = None
                tree = None

                for i in range(3):
                    last_resp = sess.get(url)

                    if not quiet:
                        tree = etree.parse(io.StringIO(last_resp.text), etree.HTMLParser())
                        fact = tree.xpath('//p[@class="lead"]')[0].text
                        print("Got a fact! '{}'".format(fact))

                    delay()

                if not tree:
                    tree = etree.parse(io.StringIO(last_resp.text), etree.HTMLParser())

                csrf_token = tree.xpath('//form[@action="/login"]/input[@name="csrf_token"]')[0].get('value')
                creds = {
                    "user": user,
                    "passwd": passwd, 
                    "csrf_token": csrf_token
                }
                
                sess.post("{}/login".format(url), data=creds).raise_for_status()
                delay()

                last_resp = sess.get(url)

                if not quiet:
                    tree = etree.parse(io.StringIO(last_resp.text), etree.HTMLParser())
                    fact = tree.xpath('//p[@class="lead"]')[0].text
                    print("Bonus Fact (flag)! '{}'".format(fact))

            except requests.exceptions.ConnectionError as err:
                print("Connection error: " + str(err))
                continue

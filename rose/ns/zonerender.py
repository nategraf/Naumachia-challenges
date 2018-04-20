#!/usr/bin/env python3
# coding: utf-8

from os import environ, path, makedirs, execvp
from time import sleep
from dns.resolver import NoAnswer as DnsNoAnswer, NXDOMAIN
from dns.exception import Timeout as DnsTimeout
import dns.resolver
import jinja2
import sys
import logging

LOG_LEVEL = environ.get('LOG_LEVEL', 'INFO')
zone_template = environ.get("ZONE_TEMPLATE", "./zone.j2")
named_template = environ.get("NAMED_TEMPLATE", "./named.conf.j2")
named_output = environ.get("NAMED_RENDERED", "/data/bind/etc/named.conf")
ttl = environ.get("ZONE_TTL", "10s")
ns = environ.get("ZONE_NS", "ns")
domain = environ["ZONE_DOMAIN"] # Domain without leading dot
hostnames = environ["ZONE_HOSTS"].split() # Space seperated list
zone_output = environ.get("ZONE_RENDERED", "/data/bind/etc/{}.zone".format(domain))

_levelnum = getattr(logging, LOG_LEVEL.upper(), None)
if not isinstance(_levelnum, int):
    raise ValueError('Invalid log level: {}'.format(LOG_LEVEL))

logging.basicConfig(level=_levelnum, format="[%(levelname)s %(asctime)s] %(message)s", datefmt="%m-%d %H:%M:%S")
logger = logging.getLogger('zonerender')

# This resolver is going to hit the docker provider dns
resolver = dns.resolver.Resolver()

retry_delay = 5
retry_count = 3

def render(zone_template, **context):
    dirname, filename = path.split(zone_template)
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(dirname or './')
    )
    return env.get_template(filename).render(**context)

def lookup(hostname):
    attempt = 0
    while True:
        attempt = attempt + 1
        try:
            logging.info("Getting %s address from shadow...", hostname)
            answers = resolver.query(hostname, "A")
        except(DnsTimeout, DnsNoAnswer, NXDOMAIN) as err:
            logging.error("Getting %s address: FAILED %s", hostname, err)
            if attempt > retry_count:
                raise
        else:
            logging.info("Getting %s address: SUCCESS", hostname)
            return answers
        sleep(retry_delay)

def writefile(filepath, text):
    makedirs(path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(text)

if __name__ == "__main__":
    # Ensure the namesserver is in hosts and remove duplicates
    hostnames = set(hostnames)
    hostnames.add(ns)

    # Get the address of each host
    hosts = dict()
    for hostname in hostnames:
        hosts[hostname] = lookup(hostname + '.shadow')

    # Render the zone file
    zone_text = render(zone_template, ns=ns, hosts=hosts, domain=domain, ttl=ttl)
    writefile(zone_output, zone_text)
    logging.info("Rendered zone file for %s", domain)
    logging.debug(zone_text)

    # Render the named.conf file
    named_text = render(named_template, domain=domain)
    writefile(named_output, named_text)
    logging.info("Rendered named.conf")
    logging.debug(named_text)

    # Exec the next program
    logging.info("Done rendering zone files. Now running '%s'" % " ".join(sys.argv[1:]))
    if len(sys.argv) > 1:
        execvp(sys.argv[1], sys.argv[1:])

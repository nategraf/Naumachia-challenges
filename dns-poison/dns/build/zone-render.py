import dns.resolver
from dns.resolver import NoAnswer as DnsNoAnswer, NXDOMAIN
from dns.exception import Timeout as DnsTimeout
import jinja2
import sys
from os import environ, path, makedirs
from time import sleep

domain = environ.get("ZONE_DOMAIN") # Domain without leading dot
zone_template = environ.get("ZONE_TEMPLATE", "./zone.j2")
zone_output = environ.get("ZONE_RENDERED", "/data/bind/etc/{}.zone".format(domain))
named_template = environ.get("NAMED_TEMPLATE", "./named.conf.j2")
named_output = environ.get("NAMED_RENDERED", "/data/bind/etc/named.conf")
hostnames = environ.get("ZONE_HOSTS").split() # Space seperated list
ttl = environ.get("ZONE_TTL", "10s")
ns = environ.get("ZONE_NS", "ns")

# This resolver is going to hit the docker provider dns
resolver = dns.resolver.Resolver()

retry_delay = 5
retry_count = 3

_print = print
def print(*args, **kwargs):
    _print(*args, **kwargs)
    sys.stdout.flush()

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
            print("Getting {} address from docker:".format(hostname), end=" ")
            answers = resolver.query(hostname, "A")
        except(DnsTimeout, DnsNoAnswer, NXDOMAIN) as err:
            print("FAILED {}".format(err))
            if attempt > retry_count:
                raise
        else:
            print("SUCCESS")
            return answers
        sleep(retry_delay)

if __name__ == "__main__":

    # Ensure the namesserver is in hosts and remove duplicates
    hostnames.append(ns)
    hostanmes = set(hostnames)

    hosts = dict()
    for hostname in hostnames:
        hosts[hostname] = lookup(hostname + '.docker')

    zone_text = render(zone_template, ns=ns, hosts=hosts, domain=domain, ttl=ttl)

    print("Rendered the following zone file for {}".format(domain))
    print(zone_text)

    makedirs(path.dirname(zone_output), exist_ok=True)
    with open(zone_output, 'w') as zonefile:
        zonefile.write(zone_text)

    named_text = render(named_template, domain=domain)

    print("Rendered the following named.conf")
    print(named_text)

    makedirs(path.dirname(named_output), exist_ok=True)
    with open(named_output, 'w') as namedfile:
        namedfile.write(named_text)

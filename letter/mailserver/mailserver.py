# coding: utf-8
from os import path, environ
from aiosmtpd.smtp import SMTP
from aiosmtpd.handlers import Debugging as DebugHandler
import asyncio
import functools
import logging
import ssl

SMTPD_ADDR = environ.get('SMTPD_ADDR', '0.0.0.0')
SMTPD_PORT = int(environ.get('SMTPD_PORT', 25))
TLS_CERT = environ.get('TLS_CERT', 'cert.pem')
TLS_KEY = environ.get('TLS_KEY', 'key.pem')
LOG_LEVEL = environ.get('LOG_LEVEL', 'INFO')

_levelnum = getattr(logging, LOG_LEVEL.upper(), None)
if not isinstance(_levelnum, int):
    raise ValueError('Invalid log level: {}'.format(LOG_LEVEL))

logging.basicConfig(level=_levelnum, format="[%(levelname)s %(asctime)s] %(message)s", datefmt="%m-%d %H:%M:%S")
logger = logging.getLogger('mailserver')

if __name__ == "__main__":
    # Create the TLS context
    tls_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    tls_context.load_cert_chain(TLS_CERT, TLS_KEY)

    # Initialize the server
    loop = asyncio.get_event_loop()
    factory = functools.partial(SMTP, DebugHandler(), tls_context=tls_context)
    coro = loop.create_server(factory, SMTPD_ADDR, SMTPD_PORT)
    server = loop.run_until_complete(coro)

    # Run the server until stopped
    logger.info('Starting SMTPd sever listening on %s:%d', SMTPD_ADDR, SMTPD_PORT)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Shutdown
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

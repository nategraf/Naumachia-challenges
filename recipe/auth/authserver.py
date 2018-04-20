# coding: utf-8
from os import path, environ
import asyncio
import jwt
import yaml
import logging

AUTH_ADDR = environ.get('AUTH_ADDR', '0.0.0.0')
AUTH_PORT = int(environ.get('AUTH_PORT', 4505))
USERS_FILE = environ.get('USERS_FILE', path.join(path.dirname(path.realpath(__file__)), 'users.yml'))
SECRET = environ.get('SECRET')
LOG_LEVEL = environ.get('LOG_LEVEL', 'INFO')

_levelnum = getattr(logging, LOG_LEVEL.upper(), None)
if not isinstance(_levelnum, int):
    raise ValueError('Invalid log level: {}'.format(LOG_LEVEL))

logging.basicConfig(level=_levelnum, format="[%(levelname)s %(asctime)s] %(message)s", datefmt="%m-%d %H:%M:%S")
logger = logging.getLogger('authserver')

class ProtocolError(Exception):
    def __init__(self, message):
        self.msg = msg
        super().__init__(message)

class FtpAuthServerProtocol(asyncio.Protocol):
    nonces = set()

    def __init__(self, users, secret):
        self.users = users
        self.secret = secret

    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        self.transport = transport
        logger.debug("%s | Connected", self.peername)

    def connection_lost(self, exc):
        logger.debug("%s | Disconnected", self.peername)

    def validate_required(self, msg, *required):
        for key in required:
            if key not in msg:
                raise ProtocolError("Invalid request: missing '{}' field".format(key))

    def respond_auth(self, msg):
        self.validate_required(msg, 'user')

        # Attempt to resolve the username
        authenticated = False
        user = self.users.get(msg['user'], None)

        # Check the password
        if user is not None:
            if user.password is None:
                authenticated = True
            elif 'pass' in msg:
                authenticated = msg['pass'] == user.password

        # Build the response
        return {
            'auth': authenticated
        }

    def respond_info(self, msg):
        self.validate_required(msg, 'user')

        # Attempt to resolve the username
        user = self.users.get(msg['user'], None)

        if user is not None:
            return {
                'home': user.home,
                'perm': user.permissions
            }
        else:
            raise ProtocolError("User does not exist")

    def respond_exists(self, msg):
        self.validate_required(msg, 'user')

        # Check if there is an object in the user dictionary
        return { 'exists': self.users.get(msg['user'], None) is not None }

    def respond(self, data):
        # Attempt to decode the message
        try:
            msg = jwt.decode(data, None, verify=False)
            logger.info('%s > %s', self.peername, msg)
        except jwt.exceptions.DecodeError as e:
            logger.info('%s > DecodeError [%s]: %s', self.peername, e, data)
            raise ProtocolError('Invalid JWT: ' + str(e))

        self.validate_required(msg, 'req')

        request = msg['req']
        if request == 'auth':
            return self.respond_auth(msg)
        if request == 'info':
            return self.respond_info(msg)
        if request == 'exists':
            return self.respond_exists(msg)
        else:
            return ProtocolError("Invalid request: unrecognized request type '{}' (types: auth, info, exists)".format(request))

    def data_received(self, data):
        try:
            resp = self.respond(data)
        except ProtocolError as e:
            resp = {'err': e.msg}

        logger.info('%s < %s', self.peername, resp)
        self.transport.write(jwt.encode(resp, self.secret))
        self.transport.close()

class Factory:
    def __init__(self, cls, *args, **kwargs):
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.cls(*self.args, **self.kwargs)

class User:
    def __init__(self, name, password, permissions, home):
        self.name = name
        self.password = password
        self.permissions = permissions
        self.home = home

if __name__ == "__main__":
    if SECRET is None:
        raise ValueError("SECRET must be set")

    # Set up the users dict
    with open(USERS_FILE, 'r') as f:
        users_yml = yaml.load(f.read())
    users = {name: User(name, attr['password'], attr['permissions'], attr['home']) for name, attr in users_yml.items()}

    # Initialize the server
    loop = asyncio.get_event_loop()
    factory = Factory(FtpAuthServerProtocol, users, SECRET)
    coro = loop.create_server(factory, AUTH_ADDR, AUTH_PORT)
    server = loop.run_until_complete(coro)

    # Run the server until stopped
    logger.info('Starting sever listening on %s:%d', AUTH_ADDR, AUTH_PORT)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Shutdown
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

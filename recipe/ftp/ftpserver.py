# coding: utf-8
from pyftpdlib.authorizers import AuthenticationFailed
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.log import logger
from socket import socket, AF_INET, SOCK_STREAM
from os import environ
import jwt
import logging

FTP_ADDR = environ.get('FTP_ADDR', '0.0.0.0')
FTP_PORT = int(environ.get('FTP_PORT', 21))
AUTH_ADDR = environ.get('AUTH_ADDR')
AUTH_PORT = int(environ.get('AUTH_PORT'))
SECRET = environ.get('SECRET')
LOG_LEVEL = environ.get('LOG_LEVEL', 'INFO')

_levelnum = getattr(logging, LOG_LEVEL.upper(), None)
if not isinstance(_levelnum, int):
    raise ValueError('Invalid log level: {}'.format(LOG_LEVEL))

logger.setLevel(_levelnum)


class User:
    def __init__(self, name, permissions, home):
        self.name = name
        self.permissions = permissions
        self.home = home

class RemoteAuthorizer:
    read_perms = "elr"
    write_perms = "adfmwMT"

    def __init__(self, remote, secret):
        self.remote = remote
        self.secret = secret
        self.users = dict()

    def exchange_jwt(self, obj):
        with socket(AF_INET, SOCK_STREAM) as sock:
            sock.connect(self.remote)
            sock.send(jwt.encode(obj, None, None))
            return jwt.decode(sock.recv(2048), self.secret, algorithms=['HS256'])

    def validate_authentication(self, username, password, handler):
        try:
            resp = self.exchange_jwt({'req': 'auth', 'user': username, 'pass': password})
        except Exception as e:
            logger.warning("Error comunicating with remote: %s", e)
            raise AuthenticationFailed("Error communicating with authentication server") from e

        if resp.get('auth', None):
            try:
                resp = self.exchange_jwt({'req': 'info', 'user': username })
            except Exception as e:
                logger.warning("Error comunicating with remote: %s", e)
                raise AuthenticationFailed("Error communicating with authentication server") from e

            home = resp.get('home', None)
            perm = resp.get('perm', None)
            if home is not None and perm is not None:
                self.users[username] = User(username, resp['perm'], resp['home'])
            else:
                logger.warning("Mangled response from auth service: %s", e)
                raise AuthenticationFailed("Error communicating with authentication server")
        else:
            raise AuthenticationFailed("Authentication failed")

    def get_home_dir(self, username):
        return self.users[username].home

    def has_user(self, username):
        try:
            resp = self.exchange_jwt({'req': 'exists', 'user': username})
        except Exception as e:
            logger.warning("Error comunicating with remote: %s", e)

        return bool(resp.get('exists', None))

    def has_perm(self, username, perm, path=None):
        return perm in self.users[username].permissions

    def get_perms(self, username):
        return self.user[username].permissions

    def get_msg_login(self, username):
        return "Welcome {!s}".format(username)

    def get_msg_quit(self, username):
        return "Bye"

    def impersonate_user(self, username, password):
        pass

    def terminate_impersonation(self, username):
        pass

if __name__ == "__main__":
    if AUTH_ADDR is None or AUTH_PORT is None or SECRET is None:
        raise ValueError("AUTH_ADDR, AUTH_PORT, and SECRET must be set")

    local, remote = (FTP_ADDR, FTP_PORT), (AUTH_ADDR, AUTH_PORT)

    auth = RemoteAuthorizer(remote, SECRET)

    class handler(FTPHandler):
        authorizer = auth

    server = FTPServer(local, handler)
    server.serve_forever()

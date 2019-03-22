# coding: utf-8
from flask import Flask, request, Response
import functools
import base64
import logging
import os

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))
USERNAME = os.environ.get('USERNAME', 'alice')
PASSWORD = os.environ.get('PASSWORD', 'password')
CTF_FLAG = os.environ.get('CTF_FLAG', 'flag{}')

logging.basicConfig(format="[%(levelname)7s %(asctime)s %(name)s] %(message)s", datefmt="%m-%d %H:%M:%S")
logger = logging.getLogger('web')
logger.setLevel(LOG_LEVEL)

app = Flask(__name__)
app.secret_key = SECRET_KEY

# HTTP basic auth code from http://flask.pocoo.org/snippets/8/
def check_auth(username, password):
    """Checks the username and password against set environment variables"""
    return username == USERNAME and password == PASSWORD

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    """Decorator used to require HTTP basic auth on a route"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/', methods=("GET",))
@requires_auth
def index():
    # TODO(nategraf): Add some flavor here. It's a little bland and chalky.
    return CTF_FLAG

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=8080)

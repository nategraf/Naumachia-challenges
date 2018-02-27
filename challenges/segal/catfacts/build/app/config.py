from os import environ

bind = "0.0.0.0:443"
workers = 1

certfile = environ.get("CERT_PATH", "/etc/ssl/localhost.crt")
keyfile = environ.get("KEY_PATH", "/etc/ssl/localhost.key")
ciphers="TLSv1.2"

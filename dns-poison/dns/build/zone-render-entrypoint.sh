#!/bin/sh

set -e

python3 /sbin/zone-render.py

echo "rendered naum.zone; now running $@"
exec "$@"

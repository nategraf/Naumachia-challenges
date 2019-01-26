#!/usr/bin/env bash

while [ -z "$PEER" ]; do
    PEER=$(dig -4tA +short client)
    sleep 1
done

echo in.telnetd:ALL EXCEPT $PEER > /etc/hosts.deny

echo "Added $PEER to hosts.deny exception. Starting $@"
exec "$@"

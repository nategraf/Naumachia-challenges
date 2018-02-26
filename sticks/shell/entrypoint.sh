#!/usr/bin/env bash

while [ -z "$PEER" ]; do
    PEER=$(dig -4tA client | grep -e '^client\.' | grep -o -e '\(\([0-9]\+\.\)\{3\}[0-9]\+\)')
    sleep 1
done

echo in.telnetd:ALL EXCEPT $PEER > /etc/hosts.deny

echo "Added client to hosts.deny exception. Starting $@"
exec "$@"

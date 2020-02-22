#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
for file in $(find . -name docker-compose.yml); do
    pushd $(dirname $file)
    sudo docker-compose build $@
    popd
done

#!/bin/bash

if ! id "$DOCKER_USER"; then
    echo 'ERROR: $DOCKER_USER "'"$DOCKER_USER"'" does not exist'
    exit 1
fi

docker compose down
docker compose build --no-cache # rebuild with no cache to apply changes
DOCKER_USER_STR="$(id -u "$DOCKER_USER"):$(id -g "$DOCKER_USER")" docker compose up

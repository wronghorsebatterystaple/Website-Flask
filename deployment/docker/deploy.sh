#!/bin/bash

if ! id "$DOCKER_USER"; then
    echo '[ERROR] $DOCKER_USER "'"$DOCKER_USER"'" does not exist'
    exit 1
fi

docker compose down
docker system prune --force
docker compose build # make sure changes in Dockerfile/build directory are always applied
DOCKER_USER_NAME="$(id -u "$DOCKER_USER"):$(id -g "$DOCKER_USER")" docker compose up

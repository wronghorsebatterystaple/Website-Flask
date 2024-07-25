#!/bin/bash

docker system prune --all --force
docker compose build --no-cache # rebuild with no cache to apply changes
docker compose up

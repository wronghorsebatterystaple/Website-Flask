#!/bin/bash

docker system prune --all --force # don't use 70GB of storage and freak me out again with old cache
docker compose build --no-cache   # rebuild with no cache to apply changes
docker compose up

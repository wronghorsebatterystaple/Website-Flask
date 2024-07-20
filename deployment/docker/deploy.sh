#!/bin/bash

docker compose build --no-cache # rebuild with no cache to apply changes
docker compose up

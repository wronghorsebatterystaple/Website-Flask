#!/bin/bash

docker build -t flask-website:latest .
docker stop flask-website # will error if not exist; it's fine
docker run --name flask-website -d -p 8008:8008 --rm --network flask-website-network flask-website:latest

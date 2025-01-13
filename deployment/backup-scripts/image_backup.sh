#!/bin/bash

set -e

# SYNC: relative path to Git repo base
for file in ../../app/blog/static/blogpage/*; do
    if [[ -d "$file/images/" ]]; then
        git add "$file/images/"
    fi
done

git commit -m "[autocommit] thank you github for free image backups <3"
git push

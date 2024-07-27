#!/bin/bash

# Uncomment for debugging
set -x

# SYNC: relative path to Git repo base
for file in ../../app/blog/static/blog/blogpage/*; do
    git add "$file/images/"
done

git commit -m "[Autocommit] Thank you GitHub for free image backups <3"
git push

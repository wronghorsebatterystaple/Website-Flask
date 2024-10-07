#!/bin/bash

# SYNC: relative path to Git repo base
for file in ../../app/blog/static/blogpage/*; do
    git add "$file/images/"
done

git commit -m "autocommit: thank you github for free image backups <3"
git push

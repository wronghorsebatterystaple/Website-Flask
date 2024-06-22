#!/bin/bash

# This will be harmless if no changes have been detected
# Note that this will auto-commit changes in the entire static directory, so gitignore preemptively or stop service
git add app/blog/static/blog/blogpage/
git commit -m "[Autocommit] Thank you GitHub for giving me free image backups <3"
git push # only works if no passcode for SSH key!

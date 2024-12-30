#!/bin/bash

while true; do
    flask db upgrade
    if [[ "$?" == '0' ]]; then
        break
    fi
    echo 'Upgrade command failed, retrying in 3 secs...'
    sleep 3
done

exec gunicorn -b :8080 -m 007 -w 4 --forwarded-allow-ips="*" --access-logfile - --error-logfile - personal_website:app

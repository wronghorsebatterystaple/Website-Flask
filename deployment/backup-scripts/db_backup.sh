#!/bin/bash

source ./db_backup_config.sh

# Uncomment for debugging
set -x

case "$1" in
    1)
        REMOTE_BACKUP_LOCATION="$REMOTE_BACKUP_LOCATION_1"
        ;;
    2)
        REMOTE_BACKUP_LOCATION="$REMOTE_BACKUP_LOCATION_2"
        ;;
    *)
        echo "Invalid option: \"$1\""
        exit 1
        ;;
esac

docker exec "$CONTAINER_NAME_MYSQL" bash -c "mysqldump -u $DATABASE_USERNAME --password=\"$DATABASE_PASSWORD\" $DATABASE_NAME"' > '"$CONTAINER_BACKUP_PATH"
docker cp "$CONTAINER_NAME_MYSQL:$CONTAINER_BACKUP_PATH" "$HOST_BACKUP_PATH"
rsync -e "ssh -i $SSH_PRIVATE_KEY_LOCATION" --backup --suffix=`date +'.%F_%H-%M-%S'` "$HOST_BACKUP_PATH" "$REMOTE_BACKUP_LOCATION"

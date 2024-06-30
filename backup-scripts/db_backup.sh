#!/bin/bash

source $PWD/backup-scripts/db_backup_config.sh

if [[ $1 == "1" ]]; then
    REMOTE_BACKUP_LOCATION=$REMOTE_BACKUP_LOCATION_1
elif [[ $1 == "2" ]]; then
    REMOTE_BACKUP_LOCATION=$REMOTE_BACKUP_LOCATION_2
else
    echo "Invalid option \"$1\""
    exit 1
fi

docker exec $CONTAINER_NAME_MYSQL bash -c "mysqldump -u $DATABASE_USERNAME --password=\"$DATABASE_PASSWORD\" $DATABASE_NAME"' > '"$CONTAINER_BACKUP_PATH"
docker cp $CONTAINER_NAME_MYSQL:$CONTAINER_BACKUP_PATH $HOST_BACKUP_PATH
rsync -e "ssh -i $SSH_PRIVATE_KEY_LOCATION" --backup --suffix=`date +'.%F_%H-%M-%S'` $HOST_BACKUP_PATH $REMOTE_BACKUP_LOCATION
# Don't delete to avoid another apocalypse; we need to have disk space anyways and it should just be overwritten

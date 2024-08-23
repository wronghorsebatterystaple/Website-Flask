#!/bin/bash

source ./db_backup_config.sh

case "$1" in
    '1')
        remote_backup_location="$remote_backup_location_1"
        ;;
    '2')
        remote_backup_location="$remote_backup_location_2"
        ;;
    *)
        echo "Invalid option: \"$1\""
        exit 1
        ;;
esac

mysqldump --protocol=tcp -u "$database_username" --password="$database_password" "$database_name" > "$host_backup_path"
rsync -e "ssh -i $ssh_private_key_location" --backup --suffix=`date +'.%F_%H-%M-%S'` "$host_backup_path" "$remote_backup_location"

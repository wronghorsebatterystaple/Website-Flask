#!/bin/bash

## Args:
##     - `$1`: destination path for backup, formatted identically to the destination path of `scp`

source ./db_backup_config.sh

mysqldump --protocol=tcp -u "$db_username" --password="$db_password" "$db_name" > "$host_backup_path"
rsync -e "ssh -i $ssh_private_key_location" --backup --suffix=`date +'.%F_%H-%M-%S'` "$host_backup_path" "$1"

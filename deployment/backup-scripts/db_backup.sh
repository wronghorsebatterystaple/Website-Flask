#!/bin/bash

# Make sure you run `ssh` to each destination host first to trust their keys! It's important to run this as the
# user which this script will run as (by default, `sudo`).
#
# Args:
#     - `$1`: destination path for backup, formatted identically to the destination path of `scp`
#     - `$2`: backup number to be appended to the backup name (make sure of this in `db_backup_config.sh`!)

source ./db_backup_config.sh

mysqldump --protocol=tcp -u "$db_username" --password="$db_password" "$db_name" > "$host_backup_path"
rsync -e "ssh -i $ssh_private_key_location" --backup --suffix=`date +'.%F_%H-%M-%S'` "$host_backup_path" "$1"

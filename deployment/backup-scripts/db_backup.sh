#!/bin/bash

# Make sure you run `ssh` to each destination host first to trust their keys! It's important to run this as the
# user which this script will run as (by default, `sudo`).
#
# Args:
#     - `$1`: destination path for backup, formatted identically to the destination path of `scp`
#     - `$2`: backup number to be appended to the backup name

source ./db_backup_config.sh

set -e

# make sure there is a secured MySQL config file providing `$db_username`'s password!
mysqldump --protocol=tcp -u "$db_username" "$db_name" > "$host_backup_path"
rsync -e "ssh -i $ssh_private_key_location" --backup --suffix=`date +'.%F_%H-%M-%S'` "$host_backup_path" "$1"

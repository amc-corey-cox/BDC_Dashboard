#!/bin/sh
set -e

# THIS SCRIPT IS DEPRECATED. PLEASE USE GOOGLE'S SNAPSHOT BACKUP INSTEAD

# pgdump the database
docker exec bdcat_database_1 /usr/bin/pg_dump -U postgres > {{ db_data_dir }}/pg_db_dump

# get all the folder and files and zip them all with the current date
TIME=`date +%b-%d-%y`
FILENAME=backup-tickets-$TIME.tar.gz    # filename with timestamp
SRCDIR={{ db_data_dir }}/               # source database directory
DESDIR={{ db_backup_data_dir }}         # destination backup directory
tar -cpzf $DESDIR/$FILENAME $SRCDIR     # tar files into backup directory

# cleanup older backups
MAX_BACKUPS=5
FILECOUNT=$(ls -l {{ db_backup_data_dir }} | wc -l)
echo "File count for {{ db_backup_data_dir }}: $FILECOUNT"
if [ $FILECOUNT -gt $MAX_BACKUPS ]; then
    find {{ nimbus_backup_data_dir }}  -mindepth 1 -mtime +15 -delete
else
    echo "Less than {{ MAX_BACKUPS }} files so nothing to delete"
fi
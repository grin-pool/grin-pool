#!/bin/bash

BACKUP_DIR="/backup"
DB_HOST="mysql"

echo "Running db backup: " $(date)

# Clean up old backups
used=$(df $BACKUP_DIR | tail -n 1 |  awk -F'%' '{print $1}' | awk '{print $5}')
while [ $used -gt 80 ]; do
    rm $(ls -rt | head -n 1)
    used=$(df $BACKUP_DIR | tail -n 1 |  awk -F'%' '{print $1}' | awk '{print $5}')
done

mysqldump -h ${DB_HOST} -p${MYSQL_ROOT_PASSWORD} --all-databases | gzip -c - > $BACKUP_DIR/full_backup.$(date "+%F-%T" |tr : '_').sql.gz
status=$?


# Report
echo "date: " $(date)
echo "Status: $status"
echo "Disk Use: " $(df -h $BACKUP_DIR | tail -n 1) 
echo "Backups: "
ls -alrt $BACKUP_DIR

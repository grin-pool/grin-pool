#!/bin/bash


cp /usr/src/grin/grin-server.toml /server/grin-server.toml


#if [ -e /server/lock.txt ]; then
#    echo "Sleeping 1 minute 30 seconds for previous instance to terminate"
#    sleep 90
#fi

cd /server
#touch lock.txt
grin server run
#rm lock.txt

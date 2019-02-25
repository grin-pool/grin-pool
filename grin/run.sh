#!/bin/bash

if [ "$NET_FLAG" = "--floonet" ]; then
    sed -i 's/chain_type = .*/chain_type = \"Floonet\"/' /usr/src/grin/grin-server.toml
fi

cp /usr/src/grin/grin-server.toml /server/grin-server.toml
cd /server

echo "Backup Chain Data"
tar czf grin.backup.$(date "+%F-%T" |tr : '_').tgz .grin

grin ${NET_FLAG} server run

#!/bin/bash

# Update API Port for remote stratum
if [ ! -z "$APIPORT" ]; then
    sed -i "s/^api_port = .*$/api_port = ${APIPORT}/" /usr/local/bin/grin-pool.toml
fi


echo "Starting GrinPool Stratum Server"
cp /usr/local/bin/grin-pool.toml /stratum/
/usr/local/bin/grin-pool

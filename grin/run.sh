#!/bin/bash

# Live here
cd /server

# Put config file in place
cp /usr/src/grin/grin-server.toml /server/grin-server.toml

# Update grin-server config
if [ "$NET_FLAG" = "--floonet" ]; then
    # Set Network Flag in TOML Config
    sed -i 's/chain_type = .*/chain_type = \"Floonet\"/' /server/grin-server.toml
fi
if [  "$NET_FLAG" == "--floonet" ]; then
    # disable mainnet preferred peers
    sed -i 's/peers_preferred = .*$/#peers_preferred = []/' /server/grin-server.toml
fi
if [ ! -z "$WALLETPORT" ]; then
    # Update Wallet Port for remote stratum
    sed -i "s/^wallet_listener_url = .*$/wallet_listener_url = \"http:\/\/wallet:${WALLETPORT}\"/" /server/grin-server.toml
fi

#echo "Backup Chain Data"
#tar czf grin.backup.$(date "+%F-%T" |tr : '_').tgz .grin

grin ${NET_FLAG} server run

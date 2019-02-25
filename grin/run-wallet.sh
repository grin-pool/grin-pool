#!/bin/bash -x

if [ "$NET_FLAG" = "--floonet" ]; then
    sed -i 's/chain_type = .*/chain_type = \"Floonet\"/' /usr/src/grin/grin-wallet.toml
fi

# Live here
cd /wallet

# Copy in updated config
cp /usr/src/grin/grin-wallet.toml /wallet/grin-wallet.toml

# Create new wallet if none exists
if [ ! -f /wallet/wallet_data/wallet.seed ]; then
    echo ${WALLET_PASSWORD} > /password.txt
    echo ${WALLET_PASSWORD} >> /password.txt
    grin ${NET_FLAG} wallet init < /password.txt
    rm /password.txt
fi

MODE="public"
if [ $# -ne 0 ]; then
    MODE=$1
fi


if [ $MODE == "private" ]; then
    mkdir -p /root/.grin/
    echo ${WALLET_OWNER_API_PASSWORD} > /root/.grin/.api_secret
    chmod 600 /root/.grin/.api_secret
    echo "Waiting for public wallet to start"
    sleep 30 # Let the public wallet start first
    keybase login
    echo "Starting wallet owner_api"
    grin ${NET_FLAG} wallet -p ${WALLET_PASSWORD} owner_api
else
    echo "Backup Wallet DB"
    tar czf wallet_db.backup.$(date "+%F-%T" |tr : '_').tgz wallet_data
    echo "Starting public wallet listener"
    grin ${NET_FLAG} wallet -p ${WALLET_PASSWORD} listen
fi

#!/bin/bash

# It is expected that a wallet file exists

cp /usr/src/grin/grin-wallet.toml /wallet/grin-wallet.toml

cd /wallet
grin wallet init
grin wallet listen

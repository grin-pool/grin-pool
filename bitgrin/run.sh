#!/bin/bash

cp /usr/src/grin/grin-server.toml /server/grin-server.toml
cd /server
grin ${NET_FLAG} server run

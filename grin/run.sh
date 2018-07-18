#!/bin/bash

# /server can be a mounted or shared filesystem
if [ ! -e /server/grin.toml ]; then
  cp /usr/src/grin/grin.toml /server/grin.toml
fi

cd /server
#sed -i 's/^#?archive_mode = .*$/archive_mode = true/' grin.toml
sed -i 's/^run_tui = .*$/run_tui = false/' grin.toml
#sed -i 's/^api_http_addr = .*$/api_http_addr = "0.0.0.0:13413"/' grin.toml
sed -i 's/^stratum_server_addr = .*$/stratum_server_addr = "0.0.0.0:13416"/' grin.toml
sed -i 's/^api_listen_interface = .*$/api_listen_interface = "0.0.0.0"/' grin.toml
sed -i 's/^attempt_time_per_block = .*$/attempt_time_per_block = 180/' grin.toml

grin

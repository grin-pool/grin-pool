#!/bin/bash

echo "Starting GrinPool Stratum Server"
cp /usr/local/bin/grin-pool.toml /stratum/
/usr/local/bin/grin-pool

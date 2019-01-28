#!/bin/bash

echo "Starting as $1"
config="/usr/share/logstash/config/$1"

sed -i "s/RMQ_USER/${RMQ_USER}/" $config
sed -i "s/RMQ_PASSWORD/${RMQ_PASSWORD}/" $config

logstash -f $config

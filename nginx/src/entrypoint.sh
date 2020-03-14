#!/bin/bash


# Create and renew certs
bash /renew_certs.sh &


# Start nginx
nginx


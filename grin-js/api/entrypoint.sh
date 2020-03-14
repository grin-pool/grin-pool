#!/bin/bash

# Patch in the secrets
sed -i -e "s/MYSQL_ROOT_PASSWORD/$MYSQL_ROOT_PASSWORD/" /api/config/production.json

yarn sucrase && yarn serve

#!/bin/bash

while /bin/true; do

  OK=1

  /rabbitmqadmin -q import /definitions.json
  if [ $? -ne 0 ]; then
    echo "Failed to import definitions.json"
    OK=0
  fi

  rabbitmqctl add_user $RABBITMQ_USER $RABBITMQ_PASSWORD

  rabbitmqctl set_user_tags $RABBITMQ_USER administrator
  if [ $? -ne 0 ]; then
    echo "Failed to set_user_tags"
    OK=0
  fi

  rabbitmqctl set_permissions -p / $RABBITMQ_USER ".*" ".*" ".*"
  if [ $? -ne 0 ]; then
    echo "Failed to set_permissions"
    OK=0
  fi

  rabbitmqctl change_password $RABBITMQ_USER $RABBITMQ_PASSWORD
  if [ $? -ne 0 ]; then
    echo "Failed to change_password"
    OK=0
  fi
  
  if [ $OK -eq 1 ]; then
    exit 0
  fi

  sleep 20
done

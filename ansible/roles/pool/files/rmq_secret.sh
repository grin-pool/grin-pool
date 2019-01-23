#!/bin/bash
  
# RMQ password 
echo -n "username" > ./username.txt
echo -n "password" > ./password.txt
kubectl create secret generic rmq --from-file=./username.txt --from-file=./password.txt
rm ./username.txt ./password.txt

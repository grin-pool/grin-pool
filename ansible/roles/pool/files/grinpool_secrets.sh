#!/bin/bash
  
# Grin Owner-API 
echo -n "username" > ./username.txt
echo -n "password" > ./password.txt
kubectl create secret generic wallet-owner-api --from-file=./username.txt --from-file=./password.txt
rm ./username.txt ./password.txt

# GrinPool Admin
echo -n "username" > ./username.txt
echo -n "password" > ./password.txt
kubectl create secret generic grinpool-admin --from-file=./username.txt --from-file=./password.txt
rm ./username.txt ./password.txt

# google cloud storage serviceaccount json
kubectl create secret generic storage-update --from-file=grinpool-serviceaccount-storage-update.json

echo -n "password" > ./password.txt
kubectl create secret generic splunk --from-file=./password.txt
rm ./password.txt


#!/bin/bash
  
echo -n "password" > ./password.txt
kubectl create secret generic grinwallet --from-file=./password.txt
rm ./password.txt


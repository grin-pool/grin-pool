
# Set up the minikube and start the pool services/jobs:

* install and start kubernetes cluster (minikube)
* add kubernetes volumes and secrets
* start grin and mysql
* start the stratum server and pool services

Note:  You may want to update the "externalIPs" address in kubernetes spec files to match your host.


```
sudo -E minikube stop
sudo -E minikube delete
kill all kubelet processes
for f in $(docker ps -aq); do docker stop $f; docker rm $f; done
sudo -E rm -r ~/.kube ~/.minikube
sudo rm /usr/local/bin/localkube /usr/local/bin/minikube
sudo systemctl stop '*kubelet*.mount'
sudo rm -rf /etc/kubernetes/
sudo systemctl restart docker
sudo init 6

sudo vi /etc/resolv.conf
sudo -E ./minikube start --vm-driver=none

sudo mv /root/.kube $HOME/.kube
sudo chown -R $USER $HOME/.kube
sudo chgrp -R $USER $HOME/.kube
sudo mv /root/.minikube $HOME/.minikube
sudo chown -R $USER $HOME/.minikube
sudo chgrp -R $USER $HOME/.minikube

git checkout grinpool into ~/dev/grin-pool/
cd ~/dev/grin-pool/kube/secrets
./mysql_password_secret.sh
kubectl create -f docker_registry_secret.yaml
cd ~/dev/grin-pool/kube/volumes
kubectl create -f local.yaml
kubectl create -f claim.yaml
cd ~/dev/grin-pool/kube
for f in *.yaml; do kubectl create -f $f; done
```

Place config files as follows:
  /data/stratum/grin-pool.toml
  /data/grin/grin.toml
  /data/services/config.ini
  

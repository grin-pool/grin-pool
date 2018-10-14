



# Deploy Grin-Pool to Google Cloud via Kubernetes

## Log into gcloud 
```
gcloud auth login
gcloud config set project grinpool-218920 
gcloud config configurations activate default
gcloud config set compute/zone us-west1-c
```

## Create a k8s cluster
```
gcloud container clusters create grinpool  --enable-cloud-logging --disk-size=25G --machine-type=n1-standard-2 --num-nodes=6 --zone us-west1-c  
```

## Add 3 grin nodes
```
cd /root/grin-pool/ansible/roles/pool/files/
kubectl create -f grin_set.yaml 
```

## Add 3-node SQL cluster with replication
```
kubectl create -f mysql_svc.yaml
kubectl create -f mysql_configmap.yaml
kubectl create -f mysql_set.yaml
```

## Start the blockWatcher service
```
kubectl create -f blockWatcher.yaml
```

## Start the grinStats service
```
kubectl create -f grinStats.yaml
```

## Create and start the wallet 
```
kubectl create -f grinwallet_claim.yaml 
kubectl create -f grinwallet.yaml 
```

## Start the API
```
kubectl create -f poolAPI.yaml
```

## Start grin stats
```
kubectl create -f grinStats.yaml
```

## Start pool stats
```
kubectl create -f poolStats.yaml
```

## Start share aggregator
```
kubectl create -f shareAggr.yaml 
```

## Start the stratum server
```
kubectl create -f stratum.yaml 
```

## Start the Web UI
```
kubectl create -f webui.yaml 
```

## Create ingress ports
(not yet)


----------
https://kubernetes.io/docs/setup/turnkey/gce/

https://cloud.google.com/kubernetes-engine/docs/quickstart
https://kubernetes.io/docs/tasks/run-application/run-replicated-stateful-application/

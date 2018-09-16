# grin-pool

## What it is:
A [grin](https://github.com/mimblewimble/grin) mining pool

## How to try it:
* Supports Linux and Windows miners: [mimblewimble/grin-miner](https://github.com/mimblewimble/grin-miner) and [mozkomor/GrinGoldMiner](https://github.com/mozkomor/GrinGoldMiner)
* Configure your miner to connect to: <B>stratum.mwgrinpool.com:3333</B>
* Use your grin wallet URL as your stratum login, no password necessary
* Point your browser at [MWGrinPool.com](http://mwgrinpool.com/)
* Start your miner and watch your wallet fill with grin

### The architecture:
* Stateless Microservices

### The components:
* Pool Stratum Proxy: Rust
* Pool data processing jobs: Python3
* Pool API: Python3/Flask/nginx
* Pool Web UI: Python3/Flask/nginx/Jinja2/PyGal
* Database: MariaDB
* Build CI/CD: Docker (+ travis or jenkins?)
* Deploy: Ansible
* Orchestration: Kubernetes or systemd+cron

#### To run the pool yourself: [kube/README.md](kube/README.md)

#### To build use the Dockerfile in: [stratum](stratum/) and [grin-py](grin-py/)

### Current Status:
This project is under development, <B>~75%</B> complete, and will be ready by grin mainnet launch
Please contribute!

## Pizza and "beer" fund:
![BTC](https://ipfs.io/ipfs/QmZQxz5LdbCuyc8LcnUiCyTLzmWmHs644mAD7A91bmTzej) <sub>17Gmy9uhE6ziB1PzYT8MMY5A4va25dy3US</sub>

![XMR](https://ipfs.io/ipfs/QmTLh1DUXhNNuB4CkaTtv3VJftXaDEY7V8hYyYGVvYzMB8) <sub>43i7q6hVrMdgY21RH7nMghSPA6s5jjGXDeEmLjL3pNFfD1XBYqf6hJpWVabfGJ5ydJKdaBjKdFvMe1kaKRj5w7Ao7q7mK8v</sub>

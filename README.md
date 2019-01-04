# grin-pool

## What it is:
An Open Source Mining Pool for [Grin](https://github.com/mimblewimble/grin) MimbleWimble Cryptocurrency Implementation
* Supports Linux and Windows miners: [mimblewimble/grin-miner](https://github.com/mimblewimble/grin-miner) and [mozkomor/GrinGoldMiner](https://github.com/mozkomor/GrinGoldMiner)

## How to try it:
* [About](https://medium.com/@blade.doyle/mwgrinpool-com-a-grin-mining-pool-345d67cb8e98)
* [Linux CPU Mining Guide](https://medium.com/@blade.doyle/cpu-mining-on-mwgrinpool-com-how-to-efb9ed102bc9)
* [Linux GPU Mining Guide](https://medium.com/@blade.doyle/gpu-mining-on-mwgrinpool-com-how-to-72970e550a27)
* [How to get Paid](https://medium.com/@blade.doyle/configure-payments-on-mwgrinpool-com-how-to-7b84163ec467)
* [Gitter Discussion Group](https://gitter.im/grin-pool/Lobby)

### The architecture:
* Stateless Microservices

### The components:
* Pool Stratum Proxy: Rust
* Pool data processing jobs: Python3/SQLAlchemy
* Pool API: Python3/Flask/gunicorn/redis
* Pool Web UI: NodeJS/Electron/Bootstrap/React
* Database: MariaDB
* Build/Packaging: Docker
* Deploy: gcloud Kuberntests CLI
* Orchestration: Kubernetes
* Log collection: Splunk
* Load Balancer/Certificates: NGINS/LetsEncrypt
* Monitoring & Alerting: ?? NotYet (Icinga?)

#### To run the pool yourself: [ansible/roles/pool/files/README.md](ansible/roles/pool/files/README.md)

#### To build use the Dockerfile in: [stratum](stratum/) and [grin-py](grin-py/)

### Current Status:
* This project is under development, <B>~75%</B> complete, and will be ready by grin mainnet launch
* Please contribute!
* Join the discussion on [Gitter](https://gitter.im/grin-pool/Lobby)

## Pizza and "beer" fund:
![BTC](https://ipfs.io/ipfs/QmZQxz5LdbCuyc8LcnUiCyTLzmWmHs644mAD7A91bmTzej) <sub>17Gmy9uhE6ziB1PzYT8MMY5A4va25dy3US</sub>

![XMR](https://ipfs.io/ipfs/QmTLh1DUXhNNuB4CkaTtv3VJftXaDEY7V8hYyYGVvYzMB8) <sub>43i7q6hVrMdgY21RH7nMghSPA6s5jjGXDeEmLjL3pNFfD1XBYqf6hJpWVabfGJ5ydJKdaBjKdFvMe1kaKRj5w7Ao7q7mK8v</sub>

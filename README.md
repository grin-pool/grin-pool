# grin-pool

## What it is:
A [grin](https://github.com/mimblewimble/grin) mining pool

### The architecture:
* Stateless Microservices

### The components:
* Pool Stratum Proxy: Rust
* Pool data processing jobs: Python3
* Database: MariaDB (percona or galera cluster?)
* Build CI/CD: Docker (+ travis or jenkins?)
* Orchestration: Kubernetes or systemd+cron

#### To run: [kube/README.md](kube/README.md)

#### To build use the Dockerfile in: [stratum](stratum/) and [grin-py](grin-py/)

### Current Status:
This project is under development, ~32% complete.
Please contribute!

## How to try it:
Currently mining on **testnet3**
* Supports Linux and Windows miners: [https://github.com/mimblewimble/grin-miner](mimblewimble/grin-miner) and [https://github.com/mozkomor/GrinGoldMiner](mozkomor/GrinGoldMiner)
* Configure your miner to connect to:  grin-pool.us:3333
* Use your grin wallet URL as your login, no password necessary
* Start your miner and watch your wallet fill with grin

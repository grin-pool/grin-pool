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

#### To build use the Dockerfile in: [stratum](stratum/) and [services](services/)

### Current Status:
This project is under development, ~32% complete.
Please contribute!

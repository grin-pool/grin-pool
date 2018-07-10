# grin-pool

## What it is:
A [grin](https://github.com/mimblewimble/grin) mining pool

### The architecture:
* Stateless Microservices

### The components:
* Pool Stratum Proxy: Rust
* Pool data processing jobs: Python (rust?)
* Database: MariaDB (percona cluster?)
* Build CI/CD: Docker
* Orchestration: Kubernetes

#### To run: [kube/README.md](kube/README.md)

#### To build use the Dockerfile in: [stratum](stratum/) and [services](services/)

### Current Status:
This project is under development, ~30% complete.
Please contribute!

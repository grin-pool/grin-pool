# grin-pool

## What it is:
A grin mining pool

### The archittecture:
* Stateless Microservices

### The compoents:
* Pool Stratum Proxy: Rust
* Pool data processing jobs: Python (rust?)
* Database: MariaDB (percona cluster?)
* Build CI/CD: Docker
* Orchestration: Kubernetes

#### To run: [kube/README.md](kube/README.md)

#### To build use the Dockerfile in: [stratum](stratum/) and [services](services/) 

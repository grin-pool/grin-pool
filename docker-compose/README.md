# Deploy Grin-Pool to a single VM using docker-compose

## Provision a VM
* 2 vCPU 4G Mem minimum
* Install: git, Docker,  and docker-compose
* Static public IP address
* Open ports inbound: 80, 443, 2222, 3333
* Configure a Domain Name (set DNS A record for your domain)

## Get the grin-pool software
* git checkout git@github.com:grin-pool/grin-pool.git

## Edit Configuration (Yes, its a mess and needs to be improved)
* grin-pool/docker-compose/.env
* grin-pool/grin-js/webui/src/config.js
* grin-pool/grin-py/services/config.ini
* grin-pool/nginx/src/\*.conf
* grin-pool/stratum/grin-pool.toml
* Maybe a few others....

## Build and Run it
### Grin Node
Build and start the grin node first and give it an hour to sync
* cd grin-pool/docker-compose
* docker-compose up -d --build grin
* docker-compose logs -f

### The Pool
Build and start the pool
* cd grin-pool/docker-compose
* docker-compose up -d --build
* docker-compose logs -f

### Bugs
* You will see lots of connection errors at first pool startup.  Its normal for a few minutes
* It may be necessary to restart the pool (docker-compose down/up) a few times for new installs
* Not all services are integrated with docker-compose yet - its missing: auditor, blockvalidator, dbbackup, paymentmaker, poolblockunlocker, and tidywallet
* Grasph Rate calculations have not been updated for latest cuckaroo fork

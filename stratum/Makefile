CONTAINER := stratum
REGISTRY := docker.mwgrinpool.com:5001

build:
	docker build --network=host $(DOCKER_BUILD_FLAGS) -t $(CONTAINER) .
	docker tag $(CONTAINER):latest $(REGISTRY)/$(CONTAINER):latest
	docker push $(REGISTRY)/$(CONTAINER):latest


CONTAINER := rmq
REGISTRY := docker.lsd25.net:5000

push: build

build:
	docker build  --network=host $(DOCKER_BUILD_FLAGS) -t $(CONTAINER) .
	docker tag $(CONTAINER):latest $(REGISTRY)/$(CONTAINER):latest

push:
	docker push $(REGISTRY)/$(CONTAINER):latest

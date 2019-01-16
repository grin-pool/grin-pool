# GRIN
CONTAINER := grin
REGISTRY := docker.mwgrinpool.com:5001
TAG := latest

default: build push

build:
	docker build $(DOCKER_BUILD_FLAGS) -t $(CONTAINER):${TAG} .
	docker tag $(CONTAINER):${TAG} $(REGISTRY)/$(CONTAINER):$(TAG)

push:
	docker push $(REGISTRY)/$(CONTAINER):$(TAG)

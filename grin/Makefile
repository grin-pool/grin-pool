# GRIN
CONTAINER := grin
REGISTRY := xxx
TAG := latest

default: build

build:
	docker build $(DOCKER_BUILD_FLAGS) -t $(CONTAINER):${TAG} .
	docker tag $(CONTAINER):${TAG} $(REGISTRY)/$(CONTAINER):$(TAG)

push:
	docker push $(REGISTRY)/$(CONTAINER):$(TAG)

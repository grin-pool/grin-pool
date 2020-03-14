CONTAINER := apiv2
REGISTRY := xxx
TAG := latest

push: build

build:
	docker build $(DOCKER_BUILD_FLAGS) -t $(CONTAINER):${TAG} .

push:
	docker tag $(CONTAINER):${TAG} $(REGISTRY)/$(CONTAINER):${TAG}
	docker push $(REGISTRY)/$(CONTAINER):${TAG}

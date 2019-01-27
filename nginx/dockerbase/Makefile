CONTAINER := mwnginx-dockerbase
REGISTRY := docker.mwgrinpool.com:5001

push: build

build:
	docker build $(DOCKER_BUILD_FLAGS) -t $(CONTAINER) .
	docker tag $(CONTAINER):latest $(REGISTRY)/$(CONTAINER):latest

push:
	docker push $(REGISTRY)/$(CONTAINER):latest


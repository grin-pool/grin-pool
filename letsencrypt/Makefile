CONTAINER := letsencrypt
REGISTRY := xxx

push: build

build:
	docker build $(DOCKER_BUILD_FLAGS) -t $(CONTAINER) .

push:
	docker tag $(CONTAINER):latest $(REGISTRY)/$(CONTAINER):latest
	docker push $(REGISTRY)/$(CONTAINER):latest


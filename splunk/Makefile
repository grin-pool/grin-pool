CONTAINER1 := splunk
CONTAINER2 := universalforwarder
REGISTRY := docker.mwgrinpool.com:5001

push: build

build:
	docker build $(DOCKER_BUILD_FLAGS) -t $(CONTAINER1) -f ./Dockerfile.$(CONTAINER1) .
	docker tag $(CONTAINER1):latest $(REGISTRY)/$(CONTAINER1):latest
	docker build $(DOCKER_BUILD_FLAGS) -t $(CONTAINER2) -f ./Dockerfile.$(CONTAINER2) .
	docker tag $(CONTAINER2):latest $(REGISTRY)/$(CONTAINER2):latest

push:
	docker push $(REGISTRY)/$(CONTAINER1):latest
	docker push $(REGISTRY)/$(CONTAINER2):latest

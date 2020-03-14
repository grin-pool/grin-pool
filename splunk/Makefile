CONTAINER1 := splunk
CONTAINER2 := universalforwarder
REGISTRY := xxx

push: build

build:
	docker build $(DOCKER_BUILD_FLAGS) -t $(CONTAINER1) -f ./Dockerfile.$(CONTAINER1) .
	docker build $(DOCKER_BUILD_FLAGS) -t $(CONTAINER2) -f ./Dockerfile.$(CONTAINER2) .

push:
	docker tag $(CONTAINER1):latest $(REGISTRY)/$(CONTAINER1):latest
	docker tag $(CONTAINER2):latest $(REGISTRY)/$(CONTAINER2):latest
	docker push $(REGISTRY)/$(CONTAINER1):latest
	docker push $(REGISTRY)/$(CONTAINER2):latest

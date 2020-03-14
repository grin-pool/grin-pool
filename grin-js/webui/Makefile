CONTAINER := webui-js
REGISTRY := xxx

.PHONY: build


build:
	docker build --network=host $(DOCKER_BUILD_FLAGS) -t $(CONTAINER) .
	docker tag $(CONTAINER):latest $(REGISTRY)/$(CONTAINER):latest

push: build
push:
	docker push $(REGISTRY)/$(CONTAINER):latest

test:
	docker build --network=host $(DOCKER_BUILD_FLAGS) -t $(CONTAINER)-test .
	docker run -it --rm -p 3005:3005 -p 5000:5000 --name=bitgrin_webui webui-js-test


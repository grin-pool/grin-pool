CONTAINER := keybase
REGISTRY := xxx

push: build

update:
	rm keybase_amd64.deb
	curl -O https://prerelease.keybase.io/keybase_amd64.deb

build:
	docker build $(DOCKER_BUILD_FLAGS) -t $(CONTAINER) .

push:
	docker tag $(CONTAINER):latest $(REGISTRY)/$(CONTAINER):latest
	docker push $(REGISTRY)/$(CONTAINER):latest


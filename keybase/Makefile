CONTAINER := keybase
REGISTRY := bitgrinmining

push: build

update:
	rm keybase_amd64.deb
	curl -O https://prerelease.keybase.io/keybase_amd64.deb

build:
	docker build $(DOCKER_BUILD_FLAGS) -t $(CONTAINER) .
	docker tag $(CONTAINER):latest $(REGISTRY)/$(CONTAINER):latest

push:
	docker push $(REGISTRY)/$(CONTAINER):latest


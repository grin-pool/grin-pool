# GRIN
CONTAINER := grin
REGISTRY := docker.io/grinpool

default: build

build:
	rm Dockerfile
	curl -s https://raw.githubusercontent.com/mimblewimble/grin/master/Dockerfile | sed 's/COPY \. \..*$$/RUN git clone https:\/\/github.com\/mimblewimble\/grin.git .; git checkout master; git pull;/' > Dockerfile
	echo 'COPY run.sh /' >> Dockerfile
	echo 'ENTRYPOINT ["/run.sh"]' >> Dockerfile
	docker build $(DOCKER_BUILD_FLAGS) -t $(CONTAINER) .
	docker tag $(CONTAINER):latest $(REGISTRY)/$(CONTAINER):latest
	docker push $(REGISTRY)/$(CONTAINER):latest

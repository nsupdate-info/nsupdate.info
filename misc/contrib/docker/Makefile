MAINTAINER=nkeyapps
TAG=nsupdate.info
VER=$(shell git describe)
UWSGI_UID=700
UWSGI_GID=700
BASE_DIR='../../..'
DOCKER_DIR='misc/contrib/docker'

all: prod

prod:
	cd $(BASE_DIR); docker build --build-arg BUILD=prod --build-arg uwsgi_uid=$(UWSGI_UID) --build-arg uwsgi_gid=$(UWSGI_GID) --build-arg DOCKER_DIR=$(DOCKER_DIR) -t $(MAINTAINER)/$(TAG):$(VER) --rm -f $(DOCKER_DIR)/build/Dockerfile .
	docker tag $(MAINTAINER)/$(TAG):$(VER) $(MAINTAINER)/$(TAG):prod

release: require_tag prod release_latest
	docker push $(MAINTAINER)/$(TAG):$(VER)

release_latest:
	docker tag $(MAINTAINER)/$(TAG):$(VER) $(MAINTAINER)/$(TAG):latest
	docker push $(MAINTAINER)/$(TAG):latest

require_tag:
	@if ! git describe --exact-match; then\
	  echo "      *** Don't forget to create a tag by creating an official GitHub release.";\
	  exit 1;\
	fi

dev:
	cd $(BASE_DIR); docker build --build-arg BUILD=dev --build-arg uwsgi_uid=$(UWSGI_UID) --build-arg uwsgi_gid=$(UWSGI_GID) --build-arg DOCKER_DIR=$(DOCKER_DIR) -t $(MAINTAINER)/$(TAG):$(VER)-dev --rm -f $(DOCKER_DIR)/build/Dockerfile .
	docker tag $(MAINTAINER)/$(TAG):$(VER)-dev $(MAINTAINER)/$(TAG):dev

test: dev clean
	docker run -P --name $(TAG)-test-dev -d $(MAINTAINER)/$(TAG):dev

clean:
	-docker rm -f -v $(TAG)-test-dev

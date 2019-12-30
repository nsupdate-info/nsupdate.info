MAINTAINER=nkey
TAG=nsupdate.info
VER=$(shell git describe)
UWSGI_UID=700
UWSGI_GID=700

all: prod

prod:
	docker build --build-arg BUILD=prod --build-arg uwsgi_uid=$(UWSGI_UID) --build-arg uwsgi_gid=$(UWSGI_GID) -t $(MAINTAINER)/$(TAG):$(VER) --rm -f ./build/Dockerfile .
	docker tag $(MAINTAINER)/$(TAG):$(VER) $(MAINTAINER)/$(TAG):prod

release:
	docker push $(MAINTAINER)/$(TAG):$(VER)
	docker push $(MAINTAINER)/$(TAG):prod
	@echo "*** Don't forget to create a tag by creating an official GitHub release."

release_latest:
	docker tag $(MAINTAINER)/$(TAG):$(VER) $(MAINTAINER)/$(TAG):latest
	docker push $(MAINTAINER)/$(TAG):latest

release_stable:
	docker tag $(MAINTAINER)/$(TAG):$(VER) $(MAINTAINER)/$(TAG):stable
	docker push $(MAINTAINER)/$(TAG):stable

dev:
	docker build --build-arg BUILD=dev --build-arg uwsgi_uid=$(UWSGI_UID) --build-arg uwsgi_gid=$(UWSGI_GID) -t $(MAINTAINER)/$(TAG):$(VER)-dev --rm -f ./build/Dockerfile .
	docker tag $(MAINTAINER)/$(TAG):$(VER)-dev $(MAINTAINER)/$(TAG):dev

test: dev clean
	docker run -P --name $(TAG)-test-dev -d $(MAINTAINER)/$(TAG):dev

clean:
	-docker rm -f -v $(TAG)-test-dev

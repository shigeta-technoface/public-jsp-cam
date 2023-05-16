USER_ID=$(shell id -u)
USER_NAME=$(shell id -un)
GROUP_ID=$(shell id -g)
GROUP_NAME=$(shell id -gn)

build:
	USER_ID=$(USER_ID) USER_NAME=$(USER_NAME) GROUP_ID=$(GROUP_ID) GROUP_NAME=$(GROUP_NAME) docker-compose build

run:
	USER_ID=$(USER_ID) USER_NAME=$(USER_NAME) GROUP_ID=$(GROUP_ID) GROUP_NAME=$(GROUP_NAME) docker-compose up -d

login:
	#docker exec -ti public-jsp-cam /bin/bash -c "cd /root/public-jsp-cam"
	docker exec -ti public-jsp-cam /bin/bash


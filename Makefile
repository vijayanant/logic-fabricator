# -----------------------------
# Logic Fabricator Makefile
# -----------------------------

IMAGE_NAME=logic-fabricator
VERSION = latest
PROJECT_DIR=$(PWD)

build:
	docker build -t $(IMAGE_NAME):$(VERSION) $(PROJECT_DIR)

test:
	docker run --rm -v $(PROJECT_DIR):/app $(IMAGE_NAME):$(VERSION) poetry run pytest

run:
	docker run --rm -v $(PROJECT_DIR):/app $(IMAGE_NAME):$(VERSION) poetry run python src/logic_fabricator/main.py

tag-dev:
	docker tag $(IMAGE_NAME):$(VERSION) $(IMAGE_NAME):dev

## Tag image as prod
tag-prod:
	docker tag $(IMAGE_NAME):$(VERSION) $(IMAGE_NAME):prod

## Push specific tag to registry
# Usage: make push TAG=dev
push:
	docker push $(IMAGE_NAME):$(TAG)

## Remove all local tags (optional cleanup)
clean:
	docker rmi $(IMAGE_NAME):dev || true
	docker rmi $(IMAGE_NAME):prod || true
	docker rmi $(IMAGE_NAME):$(VERSION) || true

shell:
	docker run --rm -it -v $(PROJECT_DIR):/app $(IMAGE_NAME):$(VERSION) /bin/bash

rebuild: clean build


# -----------------------------
# Logic Fabricator Makefile
# -----------------------------

IMAGE_NAME=logic-fabricator
VERSION = latest
PROJECT_DIR=$(PWD)

build:
	docker build -t $(IMAGE_NAME):$(VERSION) $(PROJECT_DIR)

test:
	docker compose --profile test run --rm test poetry run pytest -m "not llm"

test-all:
	docker compose --profile test run --rm test poetry run pytest

run:
	docker compose --profile dev run --rm dev poetry run logic-fabricator

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
	docker compose --profile dev run --rm dev /bin/bash

rebuild: clean build
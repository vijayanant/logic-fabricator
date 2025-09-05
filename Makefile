# -----------------------------
# Logic Fabricator Makefile
# -----------------------------

IMAGE_NAME=logic-fabricator
VERSION = latest
PROJECT_DIR=$(PWD)

build:
	docker build -t $(IMAGE_NAME):$(VERSION) $(PROJECT_DIR)

test-unit:
	docker run --rm --env-file .env.test -v $(PROJECT_DIR):/app $(IMAGE_NAME):$(VERSION) poetry run pytest -m "not llm and not db"

test-ci: test-unit

test-integration:
	# docker compose --env-file .env.test --profile test up --exit-code-from app-test --abort-on-container-exit
	docker compose --env-file .env.test --profile test run --rm app-test poetry run pytest -m "not llm" && docker compose --env-file .env.test --profile test down

run:
	docker compose --env-file .env.dev --profile dev run --rm app-dev poetry run logic-fabricator

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
	docker compose --profile dev run --rm app-dev /bin/bash

rebuild: clean build

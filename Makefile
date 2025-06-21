.PHONY: dev build deploy

dev:
	ENV=development BUCKET_NAME=$(terraform output -raw ytdl_storage_bucket) ./.venv/bin/python ./dev.py

build:
	./build.sh

deploy:
	./deploy.sh

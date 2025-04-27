#!/bin/bash
set -e

source ./.env

./build.sh

terraform init
terraform apply -auto-approve

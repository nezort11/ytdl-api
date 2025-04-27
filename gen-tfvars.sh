#!/bin/bash

echo "🔧 Generating terraform.tfvars..."

cat <<EOF > terraform.tfvars
yc_zone             = "ru-central1-a"
yc_token            = "$(yc iam create-token)"
yc_cloud_id         = "$(yc resource-manager cloud list --format json | jq -r '.[0].id')"
yc_folder_id        = "$(yc resource-manager folder list --format json | jq -r '.[0].id')"
service_account_id  = "ajevd55ctr0vldu7qfo3"
EOF

echo "✅ Done: terraform.tfvars"

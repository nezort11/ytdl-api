# https://registry.terraform.io/providers/yandex-cloud/yandex/latest/docs
terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
      version = "0.138.0"
    }
  }
}

provider "yandex" {
  service_account_key_file = "${path.module}/sakey.json"
#   token     = var.yc_token
  cloud_id  = var.yc_cloud_id
  folder_id = var.yc_folder_id
  zone      = var.yc_zone  # "ru-central1-a"
#   ymq_access_key = var.ymq_access_key
#   ymq_secret_key = var.ymq_secret_key
}

resource "yandex_storage_bucket" "ytdl-env" {
  bucket    = "ytdl-env"
  max_size  = 1073741824 # 1GB
}

resource "yandex_storage_bucket" "ytdl-storage" {
  bucket    = "ytdl-storage"
  max_size  = 5368709120 # 5GB
}

resource "yandex_function" "ytdl-function" {
  name       = "ytdl-function"
  user_hash  = filebase64sha256("ytdl-function.zip")
  runtime    = "python312"
  entrypoint = "main.handler"
  service_account_id = var.service_account_id
  environment = {
    BUCKET_NAME = yandex_storage_bucket.ytdl-storage.bucket
  }

  memory = 2048
  execution_timeout = 120
  concurrency = 3

  content {
    zip_filename = "ytdl-function.zip"
  }

  mounts {
    name = "storage"
    mode = "rw"
    object_storage {
      bucket = yandex_storage_bucket.ytdl-storage.bucket
    }
  }
  mounts {
    name = "env"
    mode = "rw"
    object_storage {
      bucket = yandex_storage_bucket.ytdl-env.bucket
    }
  }
}

# API to transform events into API Gateway v1 HTTP format for cloud function
resource "yandex_api_gateway" "ytdl-function-gateway" {
  name        = "ytdl-function-gateway"
  description = "API Gateway for ytdl-function"

  spec = <<EOF
openapi: 3.0.0
info:
  title: ytdl-function-gateway
  version: 1.0.0
paths:
  /download:
    get:
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: ${yandex_function.ytdl-function.id}
        service_account_id: ${var.service_account_id}
  /info:
    get:
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: ${yandex_function.ytdl-function.id}
        service_account_id: ${var.service_account_id}
EOF
}

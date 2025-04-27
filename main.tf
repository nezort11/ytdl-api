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
}

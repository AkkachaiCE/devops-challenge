terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = var.region
  access_key                  = var.access_key
  secret_key                  = var.secret_key
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
  s3_use_path_style           = true

  endpoints {
    iam        = var.iam_endpoint
    s3         = var.s3_endpoint
    ec2        = var.ec2_endpoint
    cloudwatch = var.cloudwatch_endpoint
  }
}

locals {
  bucket_name = "logging-application-082929"
}

module "aws_s3_bucket" {
  source      = "./modules/aws_s3"
  bucket_name = local.bucket_name
}

module "aws_iam_user_policy_attachment" {
  source          = "./modules/aws_iam"
  user_name       = "application"
  s3_bucket_name  = local.bucket_name
}

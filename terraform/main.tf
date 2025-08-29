terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region     = var.region
  access_key = var.access_key
  secret_key = var.secret_key
  endpoints {
    iam        = var.iam_endpoint
    s3         = var.s3_endpoint
    ec2        = var.ec2_endpoint
    cloudwatch = var.cloudwatch_endpoint
  }
}
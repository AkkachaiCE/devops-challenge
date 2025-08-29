terraform {

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
  s3_use_path_style = true

  endpoints {
    iam        = "http://localstack:4566"
    s3         = "http://localstack:4566"
    ec2        = "http://localstack:4566"
    cloudwatch = "http://localstack:4566"
  }
}

# module "aws_s3_bucket" {
#   source = "./modules/aws_s3"
# }

# module "aws_iam_user_policy_attachment" {
#   source = "./modules/aws_iam"
# }
resource "aws_s3_bucket" "local_bucket" {
  bucket = "logging-application-082929"
}

resource "aws_s3_bucket_versioning" "bucket_versioning" {
  bucket = "logging-application-082929"

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_iam_user" "application_user" {
  name = "application"
}

resource "aws_iam_policy" "s3_rw_policy" {
  name        = "application-s3-read-write"
  description = "Allow read/write access to existing S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::logging-application-082929",
          "arn:aws:s3:::logging-application-082929/*"
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "attach_s3_policy" {
  user       = aws_iam_user.application_user.name
  policy_arn = aws_iam_policy.s3_rw_policy.arn
}

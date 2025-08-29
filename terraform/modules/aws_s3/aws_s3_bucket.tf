resource "aws_s3_bucket" "local_bucket" {
  bucket = "logging-application-082929"
}

resource "aws_s3_bucket_versioning" "bucket_versioning" {
  bucket = "logging-application-082929"

  versioning_configuration {
    status = "Enabled"
  }
}
variable "bucket_name" {
  type        = string
  description = "Name of the S3 bucket to create"
}

resource "aws_s3_bucket" "local_bucket" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "bucket_versioning" {
  bucket = aws_s3_bucket.local_bucket.bucket

  versioning_configuration {
    status = "Enabled"
  }
}

output "bucket_name" {
  value = aws_s3_bucket.local_bucket.bucket
}

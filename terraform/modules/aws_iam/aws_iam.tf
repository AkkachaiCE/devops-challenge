variable "user_name" {
  type        = string
  description = "Name of the IAM user"
}

variable "s3_bucket_name" {
  type        = string
  description = "Name of the S3 bucket to give access to"
}

resource "aws_iam_user" "application_user" {
  name = var.user_name
}

resource "aws_iam_policy" "s3_rw_policy" {
  name        = "${var.user_name}-s3-read-write"
  description = "Allow read/write access to S3 bucket ${var.s3_bucket_name}"

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
          "arn:aws:s3:::${var.s3_bucket_name}",
          "arn:aws:s3:::${var.s3_bucket_name}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "attach_s3_policy" {
  user       = aws_iam_user.application_user.name
  policy_arn = aws_iam_policy.s3_rw_policy.arn
}

output "user_name" {
  value = aws_iam_user.application_user.name
}

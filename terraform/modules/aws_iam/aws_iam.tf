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
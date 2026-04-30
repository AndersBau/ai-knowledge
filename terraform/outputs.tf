output "aws_account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  value = var.aws_region
}

output "bucket_name" {
  value = aws_s3_bucket.documents.bucket
}

output "aws_account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  value = var.aws_region
}

output "bucket_name" {
  value = aws_s3_bucket.documents.bucket
}

output "ec2_public_ip" {
  value = aws_instance.app_server.public_ip
}

output "ec2_public_dns" {
  value = aws_instance.app_server.public_dns
}

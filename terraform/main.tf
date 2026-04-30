data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

resource "aws_s3_bucket" "documents" {
  bucket = "${var.project_name}-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}"

  tags = {
    Name        = "${var.project_name}-bucket"
    Project     = var.project_name
    Environment = "dev"
  }
}

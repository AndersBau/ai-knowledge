variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for naming AWS resources"
  type        = string
  default     = "ai-knowledge"
}
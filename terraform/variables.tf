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

variable "docker_image" {
  description = "Docker image for the Flask app"
  type        = string
  default     = "anderdeveloper/ai-knowledge:latest"
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}
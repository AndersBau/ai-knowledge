data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "app_server" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t2.micro"

  vpc_security_group_ids = [
    aws_security_group.app_sg.id
  ]

  tags = {
    Name        = "${var.project_name}-app-server"
    Project     = var.project_name
    Environment = "dev"
  }
}

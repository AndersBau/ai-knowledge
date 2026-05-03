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

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  vpc_security_group_ids = [
    aws_security_group.app_sg.id
  ]

  user_data = <<-EOF
#!/bin/bash
dnf update -y
dnf install -y docker

systemctl enable docker
systemctl start docker

docker pull ${var.docker_image}

docker rm -f ai-knowledge || true

docker volume create ai-knowledge-data

docker run --rm \
  -v ai-knowledge-data:/app/instance \
  -e FLASK_DEBUG=false \
  -e SECRET_KEY=dev-secret-key \
  -e OPENAI_API_KEY=${var.openai_api_key} \
  ${var.docker_image} \
  python -m scripts.init_db

docker run -d \
  --name ai-knowledge \
  -v ai-knowledge-data:/app/instance \
  -p 5000:5000 \
  -e FLASK_DEBUG=false \
  -e SECRET_KEY=dev-secret-key \
  -e OPENAI_API_KEY=${var.openai_api_key} \
  ${var.docker_image}
EOF

  tags = {
    Name        = "${var.project_name}-app-server"
    Project     = var.project_name
    Environment = "dev"
  }
}

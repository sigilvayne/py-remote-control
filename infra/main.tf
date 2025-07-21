provider "aws" {
  region = var.aws_region
}

resource "aws_security_group" "allow_http" {
  name        = "control-center-sg"
  description = "Allow 8000 and SSH"

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "control_center" {
  ami               = var.instance_ami
  instance_type     = var.instance_type
  key_name          = var.key_name 
  security_groups   = [aws_security_group.allow_http.name]
  associate_public_ip_address = true

  tags = {
    Name = "ControlCenter"
  }
}


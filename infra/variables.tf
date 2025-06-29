variable "aws_region" {
  default = "eu-north-1"
}

variable "instance_type" {
  default = "t3.micro"
}

variable "instance_ami" {
  default = "ami-00c8ac9147e19828e"
}

variable "key_name" {
  description = "Name of existing EC2 key pair in AWS"
}

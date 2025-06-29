output "instance_public_ip" {
  description = "Public IP of the Control Center EC2 instance"
  value       = aws_instance.control_center.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of the Control Center EC2 instance"
  value       = aws_instance.control_center.public_dns
}

provider "aws" {
  profile = var.profile
  region  = var.region
}

terraform {
  backend "s3" {
    bucket  = "lab6mitpa"
    key     = "terraform.tfstate"
    region  = "us-east-2"
    profile = "terraform"
  }
}

data "aws_key_pair" "keys" {
  key_name   = "Default_key"
  include_public_key = true
}

resource "aws_instance" "ec2_instance" {
    ami = "ami-0d8f6eb4f641ef691"
    instance_type = "t2.micro"
    key_name = data.aws_key_pair.keys.key_name
} 

output "instance_ip_addr" {
  value = aws_instance.ec2_instance.public_ip
} 
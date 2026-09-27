provider "aws" {
  region = "eu-west-1"
}

# S3 bucket for storing model artifacts and data
resource "aws_s3_bucket" "ml_artifacts" {
  bucket = "aml-mlops-artifacts"
  tags = {
    Project     = "AML-Fraud-Detection"
    Environment = "production"
  }
}

# ECR repository for Docker images
resource "aws_ecr_repository" "aml_api" {
  name                 = "aml-fraud-detection"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
}

# EKS cluster for running containers
resource "aws_eks_cluster" "aml_cluster" {
  name     = "aml-mlops-cluster"
  role_arn = aws_iam_role.eks_role.arn
  vpc_config {
    subnet_ids = var.subnet_ids
  }
}

# IAM role for EKS
resource "aws_iam_role" "eks_role" {
  name = "aml-eks-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}

# CloudWatch for logging
resource "aws_cloudwatch_log_group" "aml_logs" {
  name              = "/aml/fraud-detection"
  retention_in_days = 30
}

variable "subnet_ids" {
  description = "Subnet IDs for EKS cluster"
  type        = list(string)
  default     = []
}
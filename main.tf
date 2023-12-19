provider "aws" {
  region = "us-east-1"
}

resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.app_name}_lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com",
        },
      },
    ],
  })
}

resource "aws_iam_policy" "lambda_execution_policy" {

  name         = "${var.app_name}_lambda_execution_policy"
  path         = "/"
  description  = "AWS IAM Policy for ${var.app_name} app lambdas"
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:BatchWriteItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchGetItem",
        ],
        "Resource": [
          "arn:aws:logs:*:*:*",
          aws_dynamodb_table.shotsgained.arn
        ],
        "Effect": "Allow"
      }
    ]
  })
}

module "create_user_endpoint" {
  source = "./modules/endpoint/"
  lambda_dir = "./python/create_user"
  lambda_name = "create_user"
  lambda_role = aws_iam_role.lambda_execution_role
  lambda_policy = aws_iam_policy.lambda_execution_policy
  endpoint_description = "Create a new user"
}

module "read_user_endpoint" {
  source = "./modules/endpoint/"
  lambda_dir = "./python/read_user"
  lambda_name = "read_user"
  lambda_role = aws_iam_role.lambda_execution_role
  lambda_policy = aws_iam_policy.lambda_execution_policy
  endpoint_description = "Fetch the data for a given user"
}

resource "aws_dynamodb_table" "shotsgained" {
  name           = "${var.app_name}-table"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "PK"
  attribute {
    name = "PK" # primary key
    type = "S"  # string attribute
  }
}

# terraform backend state
# depends on creation of remote_state/main.tf
terraform {
  backend "s3" {
    bucket         = "shotsgained-terraform-backend"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "shotsgained-app-state"
  }
}
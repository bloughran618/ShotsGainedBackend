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

module "calc_shots_gained_endpoint" {
  source = "./modules/endpoint/"
  lambda_dir = "./python/calc_shots_gained"
  lambda_name = "calc_shots_gained"
  lambda_role = aws_iam_role.lambda_execution_role
  lambda_policy = aws_iam_policy.lambda_execution_policy
  endpoint_description = "Calculate Shots Gained for a given shot"
  layers = [aws_lambda_layer_version.shots_gained_common_lambda_layer.arn]
}

module "create_round_endpoint" {
  source = "./modules/endpoint/"
  lambda_dir = "./python/create_round"
  lambda_name = "create_round"
  lambda_role = aws_iam_role.lambda_execution_role
  lambda_policy = aws_iam_policy.lambda_execution_policy
  endpoint_description = "Create a round for a given user"
}

module "add_hole_endpoint" {
  source = "./modules/endpoint/"
  lambda_dir = "./python/add_hole"
  lambda_name = "add_hole"
  lambda_role = aws_iam_role.lambda_execution_role
  lambda_policy = aws_iam_policy.lambda_execution_policy
  endpoint_description = "Add a hole to a given round"
  layers = [aws_lambda_layer_version.shots_gained_common_lambda_layer.arn]
}

module "finish_round_endpoint" {
  source = "./modules/endpoint/"
  lambda_dir = "./python/finish_round"
  lambda_name = "finish_round"
  lambda_role = aws_iam_role.lambda_execution_role
  lambda_policy = aws_iam_policy.lambda_execution_policy
  endpoint_description = "Finish the round and aggregate all stats"
}

data "archive_file" "shots_gained_lambda_layer" {
  type        = "zip"
  source_dir  = "./python/shots_gained_common/layer/"
  output_path = "./python/shots_gained_common/layer.zip"
}

resource "aws_lambda_layer_version" "shots_gained_common_lambda_layer" {
  filename = data.archive_file.shots_gained_lambda_layer.output_path
  layer_name = "shots_gained_common_lambda_layer"
  compatible_runtimes = ["python3.9"]

  source_code_hash = data.archive_file.shots_gained_lambda_layer.output_base64sha256
}

resource "aws_dynamodb_table" "shotsgained" {
  name           = "${var.app_name}-table"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "PK"
  range_key     = "SK"
  attribute {
    name = "PK" # primary key
    type = "S"  # string attribute
  }
  attribute {
    name = "SK" # secondary key
    type = "S"  # string attribute
  }
  # Define global secondary index for querying by different attributes
  global_secondary_index {
    name               = "GSI1"
    hash_key           = "SK"
    range_key          = "PK"
    projection_type    = "ALL"
    write_capacity     = 5
    read_capacity      = 5
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
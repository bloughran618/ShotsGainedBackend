resource "aws_lambda_function" "create_user" {
  function_name = "${var.app_name}_${var.lambda_name}"
  handler      = "${var.lambda_name}.lambda_handler"
  runtime      = "python3.9"
  filename     = data.archive_file.zip_the_python_code.output_path
  role = var.lambda_role.arn
  source_code_hash = data.archive_file.zip_the_python_code.output_base64sha256

  depends_on = [
    aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role,
    data.archive_file.zip_the_python_code
  ]
}

#resource "aws_iam_role" "lambda_execution_role" {
#  name = "${var.app_name}_lambda_execution_role"
#
#  assume_role_policy = jsonencode({
#    Version = "2012-10-17",
#    Statement = [
#      {
#        Action = "sts:AssumeRole",
#        Effect = "Allow",
#        Principal = {
#          Service = "lambda.amazonaws.com",
#        },
#      },
#    ],
#  })
#}
#
#resource "aws_iam_policy" "lambda_execution_policy" {
#
#  name         = "${var.app_name}_lambda_execution_policy"
#  path         = "/"
#  description  = "AWS IAM Policy for ${var.app_name} app lambdas"
#  policy = jsonencode({
#    "Version": "2012-10-17",
#    "Statement": [
#      {
#        "Action": [
#          "logs:CreateLogGroup",
#          "logs:CreateLogStream",
#          "logs:PutLogEvents",
#          "dynamodb:PutItem",
#          "dynamodb:UpdateItem",
#          "dynamodb:BatchWriteItem",
#          "dynamodb:GetItem",
#          "dynamodb:Query",
#          "dynamodb:Scan",
#          "dynamodb:BatchGetItem",
#        ],
#        "Resource": [
#          "arn:aws:logs:*:*:*",
#          var.dynamo_arn
#        ],
#        "Effect": "Allow"
#      }
#    ]
#  })
#}

resource "aws_iam_role_policy_attachment" "attach_iam_policy_to_iam_role" {
  role        = var.lambda_role.name
  policy_arn  = var.lambda_policy.arn
}

resource "null_resource" "install_dependencies" {
  provisioner "local-exec" {
    command = "pip install -r ${var.lambda_dir}/requirements.txt -t ${var.lambda_dir}/"
  }

  triggers = {
    timestamp = timestamp()
  }
}

data "archive_file" "zip_the_python_code" {
  depends_on = [null_resource.install_dependencies]
  excludes   = [
    "__pycache__",
    "venv",
  ]

  type        = "zip"
  source_dir  = var.lambda_dir
  output_path = "${var.lambda_dir}/${var.lambda_name}.zip"
}
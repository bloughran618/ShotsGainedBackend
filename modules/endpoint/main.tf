resource "aws_lambda_function" "lambda" {
  function_name = "${var.app_name}_${var.lambda_name}"
  handler      = "${var.lambda_name}.lambda_handler"
  runtime      = "python3.9"
  filename     = data.archive_file.zip_the_python_code.output_path
  role = var.lambda_role.arn
  layers = var.layers
  source_code_hash = data.archive_file.zip_the_python_code.output_base64sha256

  depends_on = [
    aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role,
    data.archive_file.zip_the_python_code
  ]
}

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

# Define the API Gateway
resource "aws_api_gateway_rest_api" "api_endpoint" {
  name        = "${var.app_name}_${var.lambda_name}"
  description = var.endpoint_description
}

# Define the API Gateway resource
resource "aws_api_gateway_resource" "api_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_endpoint.id
  parent_id   = aws_api_gateway_rest_api.api_endpoint.root_resource_id
  path_part   = var.lambda_name
}

# Define the API Gateway method
resource "aws_api_gateway_method" "api_method" {
  rest_api_id   = aws_api_gateway_rest_api.api_endpoint.id
  resource_id   = aws_api_gateway_resource.api_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# Define the Lambda integration with API Gateway
resource "aws_api_gateway_integration" "api_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api_endpoint.id
  resource_id             = aws_api_gateway_resource.api_resource.id
  http_method             = aws_api_gateway_method.api_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.lambda.invoke_arn
}

# Give permission for API Gateway to invoke Lambda
resource "aws_lambda_permission" "allow_api" {
  statement_id  = "AllowAPIgatewayInvokation"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "apigateway.amazonaws.com"
}

# Deploy the API Gateway
resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [aws_api_gateway_integration.api_integration]

  rest_api_id = aws_api_gateway_rest_api.api_endpoint.id
  stage_name  = "prod"
}
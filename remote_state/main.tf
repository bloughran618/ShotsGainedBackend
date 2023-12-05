# One-time backend configuration setup
# Phoenix build instructions:
# terraform init
# terraform apply

provider "aws" {
  region = "us-east-1"
}

# the s3 bucket to store the terraform state
resource "aws_s3_bucket" "terraform_state" {
  bucket = "shotsgained-terraform-backend"

  lifecycle {
    prevent_destroy = true
  }
}

# enable versioning on the bucket
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

# dynamoDB table used for state locking (preventing two people from editing backend at the same time)
resource "aws_dynamodb_table" "terraform_state_lock" {
  name           = "shotsgained-app-state"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
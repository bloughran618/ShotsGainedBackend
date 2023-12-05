variable "app_name" {
  description = "The name of the app"
  type        = string
  default     = "shotsgained"
}

variable "lambda_dir" {
  description = "The filepath to the create_user python file"
  type        = string
}

variable "lambda_name" {
  description = "The name of the create user lambda"
  type        = string
}

variable "lambda_role" {
  description = "The lambda role to assume"
  type        = any
}

variable "lambda_policy" {
  description = "The lambda policy to assume"
  type        = any
}
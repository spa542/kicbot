# Lambda
resource "aws_lambda_function" "kicbot_lambda" {
  function_name = "kicbot"
  filename       = "kicbot.zip" # Expecting local zip using zip_kicbot.sh script
  runtime       = var.runtime_env
  handler       = "kicbot_handler.lambda_handler"
  role          = aws_iam_role.lambda_exec.arn
}

# Base IAM Policy
resource "aws_iam_role" "lambda_exec" {
  name = "kicbot_lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy Attachment
resource "aws_iam_role_policy_attachment" "lambda_execution_role_attachment" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

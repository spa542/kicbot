terraform {
  cloud {

    organization = "PrivateWorkspace"

    workspaces {
      name = "kicbot_infra"
    }
  }
}

# NOTE: AWS credentials are to be configured via environment variables in Terraform cloud for this setup
provider "aws" {
  region = "us-east-1" # Configure main region
}
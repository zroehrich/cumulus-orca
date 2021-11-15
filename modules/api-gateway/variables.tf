# Variables obtained by Cumulus deployment
# Should exist in https://github.com/nasa/cumulus-template-deploy/blob/master/cumulus-tf/variables.tf
# REQUIRED
variable "prefix" {
  type        = string
  description = "Prefix used to prepend to all object names and tags."
}

variable "request_status_for_granule_invoke_arn" {
  type        = string
  description = "Invoke ARN of the request_status_for_granule lambda function"
}

variable "request_status_for_job_invoke_arn" {
  type        = string
  description = "Invoke ARN of the request_status_for_job lambda function"
}

variable "orca_catalog_reporting_invoke_arn" {
  type        = string
  description = "Invoke ARN of the orca_catalog_reporting lambda function"
}

variable "api_gateway_policy_vpc_id" {
  type        = string
  description = "VPC ID that will have access to the API gateways"
}
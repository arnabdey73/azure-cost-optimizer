variable "subscription_id" {
  description = "The subscription ID to deploy resources into"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "cost-optimizer-rg"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "West Europe"
}

variable "storage_account_name" {
  description = "Name of the storage account for cost exports"
  type        = string
}

variable "container_name" {
  description = "Name of the blob container for cost exports"
  type        = string
  default     = "cost-exports"
}

variable "workspace_name" {
  description = "Name of the Log Analytics Workspace"
  type        = string
  default     = "cost-optimizer-law"
}

variable "client_secret" {
  description = "Service Principal client secret to store in Key Vault"
  type        = string
  sensitive   = true
  default     = ""  # Should be provided during deployment
}

variable "allowed_ip_ranges" {
  description = "List of IP addresses or CIDR blocks allowed to access Key Vault"
  type        = list(string)
  default     = []  # Should be configured during deployment
}

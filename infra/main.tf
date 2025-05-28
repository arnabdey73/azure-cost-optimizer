provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# Get current client config for Key Vault access policies
data "azurerm_client_config" "current" {}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
  # Optional: Add tags for better resource management
  tags = {
    environment = "production"
    owner       = "team@example.com"
    application = "azure-cost-optimizer"
    managedBy   = "terraform"
  }
}

# Storage Account for Cost Exports
resource "azurerm_storage_account" "cost_export_sa" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
  enable_https_traffic_only = true
  
  blob_properties {
    versioning_enabled = true
    
    delete_retention_policy {
      days = 30
    }
  }
  
  tags = {
    environment = "production"
    application = "azure-cost-optimizer"
  }
}

resource "azurerm_storage_container" "export_container" {
  name                  = var.container_name
  storage_account_id    = azurerm_storage_account.cost_export_sa.id
  container_access_type = "private"
}

# Add diagnostic settings for the storage account
resource "azurerm_monitor_diagnostic_setting" "sa_diag" {
  name                       = "sa-diagnostics"
  target_resource_id         = azurerm_storage_account.cost_export_sa.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
  
  metric {
    category = "Transaction"
    enabled  = true
    retention_policy {
      enabled = true
      days    = 30
    }
  }
  
  metric {
    category = "Capacity"
    enabled  = true
    retention_policy {
      enabled = true
      days    = 30
    }
  }
}

# Add resource lock to prevent accidental deletion
resource "azurerm_management_lock" "sa_lock" {
  name       = "sa-lock"
  scope      = azurerm_storage_account.cost_export_sa.id
  lock_level = "CanNotDelete"
  notes      = "Prevents accidental deletion of storage account containing cost data"
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "law" {
  name                = var.workspace_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# Cost Management Export Schedule
resource "azurerm_cost_management_export_subscription" "daily_export" {
  name                = "dailyCostExport"
  subscription_id     = var.subscription_id
  time_frame          = "Daily"
  recurrence_interval = "Day"
  storage_container_id = azurerm_storage_container.export_container.id

  export {
    type       = "ActualCost"
    timeframe  = "MonthToDate"
    delivery {
      container_id = azurerm_storage_container.export_container.id
      delivery_type = "StorageAccount"
      storage_account_id = azurerm_storage_account.cost_export_sa.id
    }
  }

  time_period {
    start_date = "2025-01-01"
    end_date   = "2025-12-31"
  }
}

# (Optional) Budget with alert
resource "azurerm_consumption_budget_subscription" "monthly_budget" {
  name                = "monthly-budget"
  subscription_id     = var.subscription_id
  amount              = 1000
  time_grain          = "Monthly"

  notification {
    enabled         = true
    operator        = "GreaterThan"
    threshold       = 80
    contact_emails  = ["admin@example.com"]
    threshold_type  = "Percentage"
  }
}

# Azure Key Vault for securely storing credentials
resource "azurerm_key_vault" "kv" {
  name                        = "${var.resource_group_name}-kv"
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"
  purge_protection_enabled    = true
  soft_delete_retention_days  = 90
  enable_rbac_authorization   = false  # Using access policies

  # Configure network ACLs
  network_acls {
    default_action             = "Deny"
    bypass                     = "AzureServices"
    ip_rules                   = var.allowed_ip_ranges
    virtual_network_subnet_ids = []
  }
  
  tags = {
    environment = "production"
    application = "azure-cost-optimizer"
  }
}

# Grant permissions to the current user/service principal
resource "azurerm_key_vault_access_policy" "terraform_access" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  key_permissions = [
    "Get", "List", "Create", "Delete", "Update"
  ]
  
  secret_permissions = [
    "Get", "List", "Set", "Delete", "Backup", "Restore", "Recover"
  ]
  
  certificate_permissions = [
    "Get", "List", "Create", "Delete", "Update"
  ]
}

# Store the client secret securely
resource "azurerm_key_vault_secret" "client_secret" {
  name         = "azure-client-secret"
  value        = var.client_secret
  key_vault_id = azurerm_key_vault.kv.id
  
  depends_on = [
    azurerm_key_vault_access_policy.terraform_access
  ]
}

# Store the Log Analytics workspace ID
resource "azurerm_key_vault_secret" "law_id" {
  name         = "log-analytics-workspace-id"
  value        = azurerm_log_analytics_workspace.law.id
  key_vault_id = azurerm_key_vault.kv.id
  
  depends_on = [
    azurerm_key_vault_access_policy.terraform_access
  ]
}

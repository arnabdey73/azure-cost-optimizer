provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# Storage Account for Cost Exports
resource "azurerm_storage_account" "cost_export_sa" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "export_container" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.cost_export_sa.name
  container_access_type = "private"
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

# Azure Cost Optimizer - Security Best Practices

This document outlines security best practices for deploying and operating the Azure Cost Optimizer in your environment.

## Table of Contents

- [Authentication & Authorization](#authentication--authorization)
- [Data Protection](#data-protection)
- [Network Security](#network-security)
- [Secrets Management](#secrets-management)
- [Monitoring & Auditing](#monitoring--auditing)
- [Infrastructure Security](#infrastructure-security)
- [Implementation Checklist](#implementation-checklist)

## Authentication & Authorization

### Service Principal Security

When using a Service Principal for authentication:

1. **Least-Privilege Principle**: Grant only the permissions required:
   - Reader role on subscriptions to be analyzed
   - Contributor role on the Log Analytics workspace (if using VM metrics)

2. **Credential Rotation**: Rotate the service principal secret regularly:
   - Implement a quarterly rotation schedule
   - Use Azure Key Vault to store and retrieve the secret

3. **Secret Storage**: Never store secrets in code or configuration files:
   - Use environment variables as a temporary transport mechanism
   - Use Azure Key Vault for long-term storage
   - Consider certificate-based authentication instead of client secrets

### Managed Identity (Recommended)

For production deployments, use managed identities:

1. **System-Assigned Identity**: Enable system-assigned identity on your compute resource
2. **Role Assignments**: Grant the required roles to the managed identity
3. **No Secret Management**: Eliminates the need to manage secrets

Example setup for Azure Functions:
```bash
# Enable system-assigned identity on Function App
az functionapp identity assign --name "cost-optimizer-func" --resource-group "cost-optimizer-rg"

# Get the principal ID
principal_id=$(az functionapp identity show --name "cost-optimizer-func" --resource-group "cost-optimizer-rg" --query principalId --output tsv)

# Assign Reader role on subscription
az role assignment create --assignee $principal_id --role "Reader" --scope "/subscriptions/{subscription-id}"

# Assign Contributor role on Log Analytics workspace
az role assignment create --assignee $principal_id --role "Contributor" --scope "/subscriptions/{subscription-id}/resourceGroups/{rg-name}/providers/Microsoft.OperationalInsights/workspaces/{workspace-name}"
```

## Data Protection

### Storage Security

For the storage account that holds cost data:

1. **Encryption at Rest**: Ensure storage account has encryption enabled (default in Azure)
2. **Secure Transfer**: Enable "Secure transfer required" option
3. **Storage Firewall**: Restrict access using allowed IPs or VNet integration
4. **SAS Token Security**: 
   - Use short-lived SAS tokens with minimum permissions
   - Use storage access keys only for initial setup

### Key Vault Data Protection

For storing secrets in Key Vault:

1. **Soft-Delete & Purge Protection**: Enable to prevent accidental deletion
2. **Access Policies**: Use RBAC or Access Policies with minimum permissions
3. **Key Rotation**: Implement regular key rotation for all stored secrets
4. **Logging**: Enable diagnostic logs for all Key Vault operations

## Network Security

### Private Endpoints

For production environments, use private endpoints:

1. **Storage Account**: Create a private endpoint for the storage account
2. **Key Vault**: Create a private endpoint for the Key Vault
3. **Log Analytics**: Use private link for the Log Analytics workspace

Implementation example:
```terraform
resource "azurerm_private_endpoint" "storage_endpoint" {
  name                = "${var.storage_account_name}-endpoint"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.private_endpoint_subnet.id

  private_service_connection {
    name                           = "${var.storage_account_name}-connection"
    private_connection_resource_id = azurerm_storage_account.cost_export_sa.id
    is_manual_connection           = false
    subresource_names              = ["blob"]
  }
}
```

### Network Access Restrictions

1. **Storage Firewall**: Restrict access to specific IP addresses or VNets
2. **Key Vault Firewall**: Configure network ACLs to limit access
3. **Function Network Security**: If using Azure Functions, deploy in a VNet

## Secrets Management

### Azure Key Vault Integration

1. **Store All Secrets**: Move all credentials and sensitive configuration to Key Vault:
   - Service principal secrets
   - Storage account keys
   - Log Analytics keys
   - Connection strings

2. **Secure Key Vault Access**:
   - Use RBAC with Key Vault Secrets User role
   - Or use Access Policies with minimum permissions
   - Enable Key Vault auditing

3. **Secrets Rotation**:
   - Implement automated rotation for all credentials
   - Use versioning to maintain access during rotation

Example code for retrieving secrets from Key Vault:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secrets_from_keyvault(vault_url):
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=vault_url, credential=credential)
    
    # Get secrets
    client_secret = secret_client.get_secret("azure-client-secret").value
    workspace_id = secret_client.get_secret("log-analytics-workspace-id").value
    
    return client_secret, workspace_id
```

## Monitoring & Auditing

### Azure Monitor Integration

1. **Diagnostic Settings**: Enable diagnostic settings for all resources:
   - Storage account
   - Key Vault
   - Log Analytics workspace

2. **Activity Logs**: Collect activity logs for all resources:
   - Forward to a Log Analytics workspace
   - Set up alerts for security-related events

3. **Application Insights**: For Azure Functions deployment:
   - Enable Application Insights
   - Set up alerts for failures

Example Terraform configuration:
```terraform
resource "azurerm_monitor_diagnostic_setting" "kv_diag" {
  name                       = "kv-diagnostics"
  target_resource_id         = azurerm_key_vault.kv.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
  
  log {
    category = "AuditEvent"
    enabled  = true
    retention_policy {
      enabled = true
      days    = 365
    }
  }
  
  metric {
    category = "AllMetrics"
    enabled  = true
    retention_policy {
      enabled = true
      days    = 30
    }
  }
}
```

## Infrastructure Security

### Resource Protection

1. **Resource Locks**: Apply locks to prevent accidental deletion:
   ```terraform
   resource "azurerm_management_lock" "sa_lock" {
     name       = "sa-lock"
     scope      = azurerm_storage_account.cost_export_sa.id
     lock_level = "CanNotDelete"
     notes      = "Prevents accidental deletion of storage account"
   }
   ```

2. **Tagging Strategy**: Implement comprehensive tagging:
   ```terraform
   tags = {
     environment = "production"
     application = "azure-cost-optimizer"
     owner       = "operations-team"
     securityContact = "security@example.com"
     dataClassification = "internal"
   }
   ```

3. **Secure Infrastructure as Code**:
   - Use remote backend with encryption for Terraform state
   - Use CI/CD pipelines for controlled deployments
   - Scan IaC for security issues

## Implementation Checklist

Use this checklist to ensure all security best practices are implemented:

### Authentication
- [ ] Using managed identity where possible
- [ ] Service principal with minimum required permissions
- [ ] No hardcoded credentials anywhere in code
- [ ] Secret rotation process established

### Data Protection
- [ ] Storage account encryption enabled
- [ ] Secure transfer required enabled
- [ ] Key Vault soft-delete and purge protection enabled
- [ ] Data retention policies defined

### Network Security
- [ ] Storage account firewall configured
- [ ] Key Vault network ACLs configured
- [ ] Private endpoints used where appropriate
- [ ] All public endpoints secured

### Secrets Management
- [ ] All secrets stored in Key Vault
- [ ] Key Vault access properly restricted
- [ ] Secret rotation schedule established
- [ ] Key Vault diagnostic settings enabled

### Monitoring
- [ ] Diagnostic settings enabled for all resources
- [ ] Activity logs collected
- [ ] Alerts configured for security events
- [ ] Regular security review process established

### Infrastructure Protection
- [ ] Resource locks applied
- [ ] Comprehensive tagging implemented
- [ ] Infrastructure deployed via secured CI/CD
- [ ] Regular security scans of infrastructure

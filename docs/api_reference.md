# Azure Cost Optimizer - API Reference

This document provides a detailed reference for all key classes and methods in the Azure Cost Optimizer codebase.

## Table of Contents

- [Azure Client Module](#azure-client-module)
- [Config Module](#config-module)
- [Optimizer Module](#optimizer-module)
- [Integration Points](#integration-points)

## Azure Client Module

The `AzureCostClient` class is the primary interface for interacting with Azure services.

### Authentication

#### `get_credential()`

Acquires Azure authentication credential using environment variables or default authentication.

```python
def get_credential():
    """
    Acquire Azure credential. Uses environment variables for SP or defaults.
    - If AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET are set, uses ClientSecretCredential.
    - Otherwise falls back to DefaultAzureCredential (managed identity, VS Code auth, etc.).
    
    Returns:
        azure.identity.TokenCredential: Azure credential object
        
    Raises:
        Exception: If authentication fails
    """
```

### AzureCostClient Class

#### Constructor

```python
def __init__(self, subscription_id=None):
    """
    Initialize the Cost Management client.
    If subscription_id is None, fetches the first subscription from the account.
    
    Args:
        subscription_id (str, optional): Azure subscription ID
    """
```

#### Subscription Management

```python
def list_subscriptions(self):
    """
    Return a list of subscription IDs accessible by the credential.
    
    Returns:
        list[str]: List of subscription IDs
    """
```

#### Cost Management

```python
def get_cost_by_resource(self, start_date, end_date, granularity="Daily"):
    """
    Query cost data by resource between start_date and end_date (YYYY-MM-DD).
    Returns the raw response for further processing.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        granularity (str, optional): Data granularity (Daily, Monthly, etc.)
        
    Returns:
        object: Cost management query response
    """
```

```python
def get_cost_by_tag(self, tag_name, start_date, end_date):
    """
    Query cost aggregated by a specific tag.
    
    Args:
        tag_name (str): The tag key to aggregate by
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        
    Returns:
        object: Cost management query response
    """
```

```python
def query_cost_management(self, query_string):
    """
    Execute a query against Cost Management API
    
    Args:
        query_string (str): The query description or template
            
    Returns:
        list[dict]: List of result rows
    """
```

#### Log Analytics

```python
def query_log_analytics(self, query, workspace_id=None):
    """
    Execute a query against Log Analytics workspace
    
    Args:
        query (str): The KQL query string
        workspace_id (str, optional): Optional workspace ID (defaults to config)
            
    Returns:
        list[dict]: List of result rows
        
    Raises:
        ValueError: If Log Analytics workspace ID is not provided
    """
```

#### Resource Management

```python
def list_disks(self):
    """
    List all managed disks in the subscription with their attachment status
    
    Returns:
        list[dict]: List of disk details with fields:
            - id: The resource ID
            - name: The disk name
            - attachedTo: Whether the disk is attached (bool)
            - age: Age in days (int)
            - sizeGB: Size in GB (int)
            - skuName: The storage SKU name (str)
    """
```

## Config Module

The `Config` class manages application configuration.

### Constructor

```python
def __init__(self):
    """
    Configuration for Azure Cost Optimizer.
    Reads from environment variables with sensible defaults.
    Can also retrieve secrets from Azure Key Vault.
    """
```

### Key Methods

```python
def as_dict(self):
    """
    Return configuration as dict for logging or debugging.
    
    Returns:
        dict: Configuration values (sensitive values redacted)
    """
```

```python
def get_secrets_from_keyvault(self, vault_url):
    """
    Get secrets from Azure Key Vault
    
    Args:
        vault_url (str): The URL of the Key Vault
        
    Returns:
        bool: True if secrets were retrieved successfully, False otherwise
    """
```

### Configuration Properties

| Property | Description | Default |
|----------|-------------|---------|
| `subscription_id` | Azure subscription ID | From env var |
| `client_id` | Service principal client ID | From env var |
| `tenant_id` | Azure AD tenant ID | From env var |
| `client_secret` | Service principal client secret | From env var |
| `log_analytics_workspace_id` | Log Analytics workspace ID | From env var |
| `cpu_threshold` | CPU threshold for idle VM detection | 5.0 |
| `disk_age_threshold` | Age threshold for orphaned disks | 30 |
| `anomaly_percentage` | Percentage threshold for anomalies | 50.0 |
| `output_path` | Path for recommendations output | artifacts/recommendations.json |

## Optimizer Module

The optimizer module contains the core optimization functions.

### Command Line Interface

```python
def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
```

### VM Optimization

```python
def detect_idle_vms(cost_client, start_date, end_date, cpu_threshold=5):
    """
    Query Log Analytics for VM CPU metrics and identify VMs with average 
    CPU < cpu_threshold over the period.
    
    Args:
        cost_client (AzureCostClient): Azure cost client instance
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        cpu_threshold (float, optional): CPU usage threshold percentage
        
    Returns:
        list[dict]: VMs with CPU usage below threshold
    """
```

```python
def suggest_sku_resize(cost_client, start_date, end_date):
    """
    Analyze cost by VM SKU and usage metrics to recommend downsizing 
    underutilized SKUs.
    
    Args:
        cost_client (AzureCostClient): Azure cost client instance
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        
    Returns:
        list[dict]: VMs with resize recommendations
    """
```

### Disk Optimization

```python
def find_orphaned_disks(cost_client, older_than_days=30):
    """
    List managed disks not attached to any VM and older than the threshold.
    
    Args:
        cost_client (AzureCostClient): Azure cost client instance
        older_than_days (int, optional): Age threshold for orphaned disks
        
    Returns:
        list[dict]: Orphaned disks older than threshold
    """
```

### Cost Analysis

```python
def detect_cost_anomalies(cost_client, start_date, end_date):
    """
    Compare daily cost to baseline average and flag days with spikes > X%.
    
    Args:
        cost_client (AzureCostClient): Azure cost client instance
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        
    Returns:
        list[dict]: Days with anomalous cost
    """
```

### Main Function

```python
def main():
    """
    Main entry point for the cost optimizer.
    
    Parses arguments, initializes client, runs optimization modules,
    and outputs recommendations.
    """
```

## Integration Points

The Azure Cost Optimizer is designed to be extended or integrated with other systems. Here are the key integration points:

### Input Integration

- **Command Line Arguments**: For manual or scripted execution
- **Environment Variables**: For configuration and secrets
- **Azure Key Vault**: For secure storage of credentials
- **Config File**: Optional .env file support

### Output Integration

- **JSON Output**: Structured output for programmatic consumption
- **Custom Formatters**: Can be added to support different output formats
- **DevOps Integration**: Output can be consumed by Azure DevOps pipelines
- **Reporting Tools**: Output can be imported into Power BI or other reporting tools

### Extension Points

1. **Custom Optimization Rules**: Add new detection methods to the optimizer
2. **Additional Data Sources**: Integrate with other Azure services
3. **Enhanced Recommendations**: Add more sophisticated analysis algorithms
4. **Automatic Remediation**: Extend with actions to implement recommendations

# Azure Cost Optimizer - Usage Guide

This document provides comprehensive instructions for setting up, configuring, and running the Azure Cost Optimizer tool.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Authentication](#authentication)
- [Command Line Options](#command-line-options)
- [Configuration](#configuration)
- [Example Scenarios](#example-scenarios)
- [Output Format](#output-format)
- [Automation](#automation)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before using the Azure Cost Optimizer, ensure you have:

1. **Azure Subscription** with appropriate permissions:
   - Reader access to subscriptions you want to analyze
   - Contributor access for Log Analytics workspaces (if using VM metrics)

2. **Required Software**:
   - Python 3.8 or higher
   - Terraform 1.5+ (for infrastructure deployment)
   - Azure CLI (optional, for authentication)

3. **Service Principal** (if not using Managed Identity):
   - Create a service principal with appropriate permissions
   - Note the client ID, tenant ID, and client secret

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/arnabdey73/azure-cost-optimizer.git
   cd azure-cost-optimizer
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Authentication

The Azure Cost Optimizer supports multiple authentication methods:

### 1. Service Principal

Set the following environment variables:

```bash
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
```

### 2. Azure Key Vault

Store your credentials in a Key Vault and set:

```bash
export AZURE_KEY_VAULT_URL="https://your-keyvault.vault.azure.net/"
```

The application will retrieve the required secrets from Key Vault.

### 3. Managed Identity

When running in Azure (e.g., in Azure Functions or a VM), use managed identity by not setting any of the above environment variables. The application will use the DefaultAzureCredential which checks for managed identity first.

### 4. Azure CLI (Development Only)

For local development, you can use Azure CLI authentication:

```bash
az login
```

The application will use the DefaultAzureCredential which includes Azure CLI credentials.

## Command Line Options

The optimizer supports various command line options:

```bash
python src/optimizer.py --help
```

Key options include:

| Option | Description | Default |
|--------|-------------|---------|
| `--subscription-id` | Azure subscription ID to analyze | First available subscription |
| `--start-date` | Start date for cost analysis (YYYY-MM-DD) | 7 days ago |
| `--end-date` | End date for cost analysis (YYYY-MM-DD) | Today |
| `--output` | Path for JSON recommendations output | artifacts/recommendations.json |

## Configuration

### Environment Variables

Beyond authentication, the following environment variables can be set:

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_ANALYTICS_WORKSPACE_ID` | Workspace ID for Log Analytics | None |
| `CPU_THRESHOLD` | CPU percentage threshold for idle VM detection | 5 |
| `DISK_AGE_THRESHOLD_DAYS` | Days threshold for orphaned disk detection | 30 |
| `ANOMALY_PERCENTAGE_THRESHOLD` | Percentage increase for cost anomaly detection | 50 |
| `OUTPUT_PATH` | Path for recommendations output | artifacts/recommendations.json |

### Configuration File (Optional)

Instead of environment variables, you can create a `.env` file in the project root:

```
AZURE_SUBSCRIPTION_ID=subscription-id
LOG_ANALYTICS_WORKSPACE_ID=workspace-id
CPU_THRESHOLD=5
DISK_AGE_THRESHOLD_DAYS=30
ANOMALY_PERCENTAGE_THRESHOLD=50
```

## Example Scenarios

### Basic Usage

Run with default settings (analyzes last 7 days):

```bash
python src/optimizer.py
```

### Custom Date Range

Analyze a specific date range:

```bash
python src/optimizer.py --start-date 2025-04-01 --end-date 2025-04-30
```

### Multiple Subscriptions

Analyze multiple subscriptions (run separately for each):

```bash
python src/optimizer.py --subscription-id subscription-id-1
python src/optimizer.py --subscription-id subscription-id-2
```

### Custom Thresholds

Set custom thresholds via environment variables:

```bash
export CPU_THRESHOLD=10
export DISK_AGE_THRESHOLD_DAYS=60
export ANOMALY_PERCENTAGE_THRESHOLD=30
python src/optimizer.py
```

## Output Format

The optimizer generates a JSON file with the following structure:

```json
{
  "timestamp": "2025-05-28T14:30:00.000Z",
  "metadata": {
    "subscription_id": "subscription-id",
    "time_period": {
      "start_date": "2025-05-21",
      "end_date": "2025-05-28"
    },
    "thresholds": {
      "cpu_threshold": 5,
      "disk_age_threshold_days": 30,
      "anomaly_percentage": 50
    }
  },
  "idleVMs": [
    {
      "resourceId": "/subscriptions/subscription-id/resourceGroups/rg-name/providers/Microsoft.Compute/virtualMachines/vm-name",
      "averageCpu": 2.5,
      "estimatedSavings": 150.75
    }
  ],
  "skuResizes": [
    {
      "resourceId": "/subscriptions/subscription-id/resourceGroups/rg-name/providers/Microsoft.Compute/virtualMachines/vm-name",
      "currentSku": "Standard_D8s_v3",
      "suggestedSku": "Standard_D4s_v3",
      "estimatedSavings": 87.60
    }
  ],
  "orphanedDisks": [
    {
      "diskName": "unused-disk",
      "resourceGroup": "rg-name",
      "ageDays": 45,
      "sizeGB": 256,
      "skuName": "Premium_LRS",
      "estimatedSavings": 38.40
    }
  ],
  "costAnomalies": [
    {
      "date": "2025-05-15",
      "cost": 150.0,
      "baseline": 100.0,
      "percentageIncrease": 50,
      "resourceGroups": ["rg-name-1", "rg-name-2"]
    }
  ],
  "summary": {
    "totalRecommendations": 4,
    "totalEstimatedSavings": 276.75
  }
}
```

## Automation

### Azure DevOps Pipeline

For regular execution, use the included Azure DevOps pipeline:

1. Configure service connection in Azure DevOps
2. Update pipeline variables in `azure-pipelines.yml` if needed
3. Run the pipeline manually or set up a schedule

### Azure Functions

For serverless execution (requires additional setup):

1. Deploy the code to an Azure Function App
2. Set up Managed Identity for the Function App
3. Grant necessary permissions to the Managed Identity
4. Configure a timer trigger for regular execution

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Verify service principal credentials
   - Check that service principal has appropriate permissions
   - Ensure Azure CLI is logged in (for local development)

2. **Missing Log Analytics Data**:
   - Verify workspace ID is correct
   - Check that VMs are sending metrics to Log Analytics
   - Ensure queries are covering the correct time period

3. **Empty Results**:
   - Check date range parameters
   - Verify subscription has resources to analyze
   - Lower thresholds for more recommendations

### Diagnostic Logging

Set the `AZURE_DEBUG` environment variable for detailed logs:

```bash
export AZURE_DEBUG=1
python src/optimizer.py
```

### Getting Support

For issues or questions:
1. Check the GitHub repository issues
2. Submit detailed bug reports with logs and configuration
3. For urgent assistance, contact the repository maintainer

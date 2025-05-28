# Azure Cost Optimizer - Architecture

This document describes the architecture, key components, and design principles of the Azure Cost Optimizer solution.

## System Architecture

### Data Flow Diagram

```text
┌───────────────────────────┐        ┌────────────────────────┐
│ Azure Cost Management API │───▶───▶│ Log Analytics Workspace│
└───────────────────────────┘        └────────────────────────┘
           │                                      │
           ▼                                      ▼
┌───────────────────────────┐        ┌────────────────────────┐
│    Azure Storage Export   │        │   Terraform Infra as   │
│  (Cost Exports to Blob)   │        │   Code (budgets, logs) │
└───────────────────────────┘        └────────────────────────┘
           │                                      │
           ▼                                      ▼
      ┌────────────────────────────────────────────────┐
      │            Python Optimizer Service            │
      │  • Fetches cost and usage metrics              │
      │  • Runs optimization rules                     │
      │  • Generates recommendations                   │
      │  • (Optional) Creates DevOps work items        │
      └────────────────────────────────────────────────┘
```

## Core Components

### 1. Azure Client (`src/azure_client.py`)

The Azure Client is the interface for all Azure service interactions. It handles:

- **Authentication**: Uses both Service Principal and Managed Identity authentication methods
- **Cost Management API**: Queries cost data with various aggregations and filters
- **Resource Management**: Lists and analyzes Azure resources
- **Log Analytics**: Queries VM performance metrics

The client is designed with a flexible credential model, supporting:
- Environment variable configuration
- Azure Key Vault integration
- DefaultAzureCredential for local development

### 2. Configuration Manager (`src/config.py`)

The Configuration Manager handles all configuration aspects:

- **Environment Variable Loading**: Reads configuration from environment variables
- **Secret Management**: Integrates with Azure Key Vault for secure storage
- **Default Values**: Provides sensible defaults for optimization thresholds
- **Configuration Validation**: Ensures required settings are available

### 3. Optimization Engine (`src/optimizer.py`)

The Optimization Engine implements the core cost optimization logic:

- **Idle VM Detection**: Uses CPU metrics to identify underutilized VMs
- **Right-sizing Recommendations**: Analyzes VM usage patterns to suggest downsizing
- **Orphaned Disk Detection**: Finds and reports detached disks
- **Cost Anomaly Detection**: Identifies unusual spending patterns

### 4. Infrastructure as Code (`infra/`)

The Terraform configuration provisions required Azure resources:

- **Storage Account**: For cost export data storage
- **Log Analytics Workspace**: For collecting VM metrics
- **Cost Management Export**: Schedules regular cost data exports
- **Key Vault**: Securely stores credentials and configuration
- **Budget Alerts**: Configure notification thresholds for spending

## Security Architecture

The security architecture follows the Azure Well-Architected Framework:

1. **Identity & Access Management**
   - Least-privilege principle for service principals
   - Support for managed identities
   - Key Vault for secret storage

2. **Data Protection**
   - TLS 1.2+ for all connections
   - Storage account encryption at rest
   - Private endpoint support (optional)

3. **Network Security**
   - Storage account firewall configuration
   - Key Vault network ACLs
   - Support for private endpoints

4. **Operational Security**
   - Diagnostic settings for all resources
   - Resource locks to prevent accidental deletion
   - Comprehensive error handling and logging

## Scalability Considerations

The solution is designed for multi-subscription, large-scale Azure environments:

- **Parallel Processing**: For multi-subscription analysis
- **Batched Querying**: To handle large volumes of cost data
- **Incremental Analysis**: To reduce processing requirements
- **Scheduled Execution**: Via Azure Functions or AKS (not included)

## Extensibility

The architecture is designed for extensibility:

1. **Custom Optimization Rules**: New rules can be added to the optimizer
2. **Additional Data Sources**: Support for other Azure services can be added
3. **Integration Points**: Output can be customized for various systems
4. **Modular Design**: Clear separation of concerns allows component replacement

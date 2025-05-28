# Azure Cost Optimizer

![Azure Cost Optimizer](https://img.shields.io/badge/Azure-Cost%20Optimizer-0078D4?logo=microsoft-azure)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-1.5+-7B42BC?logo=terraform&logoColor=white)

A comprehensive solution for optimizing Azure costs through automated analysis of cost data, detection of idle resources, and recommendation generation for cost savings.

## Features

- **Resource Optimization**
  - Identifies idle VMs based on CPU usage metrics
  - Recommends VM SKU downsizing for cost-efficient operations
  - Detects orphaned (unattached) managed disks
  - Identifies cost anomalies by comparing against baseline spending

- **Infrastructure as Code**
  - Terraform configuration for Azure resources
  - Creates cost export schedules to Azure Storage
  - Configures Log Analytics for resource metrics collection
  - Sets up budget alerts for cost control

- **Security**
  - Azure Key Vault integration for secure credential storage
  - Support for managed identities
  - Secure storage of configuration with proper access controls

## Requirements

### Prerequisites
- Python 3.8+
- Terraform 1.5+
- Azure subscription with appropriate permissions

### Python Dependencies
See `requirements.txt` for the complete list of dependencies. Key components:
- Azure SDK libraries
- Analytics and data processing libraries
- Testing and development utilities

## Project Structure

```
azure-cost-optimizer/
│
├── docs/                          # Documentation
│   ├── architecture.md            # Solution architecture
│   └── usage.md                   # Detailed usage guide
│
├── infra/                         # Infrastructure as Code
│   ├── main.tf                    # Main Terraform configuration
│   └── variables.tf               # Terraform variables
│
├── src/                           # Source code
│   ├── __init__.py                # Package initialization
│   ├── azure_client.py            # Azure API client implementation
│   ├── config.py                  # Configuration management
│   └── optimizer.py               # Core optimization logic
│
├── tests/                         # Test suite
│   ├── __init__.py                # Test package initialization
│   ├── test_azure_client.py       # Tests for Azure client
│   └── test_optimizer.py          # Tests for optimizer logic
│
├── azure-pipelines.yml            # CI/CD pipeline configuration
├── LICENSE                        # Project license
├── README.md                      # This file
└── requirements.txt               # Python dependencies
```

## Getting Started

### Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/arnabdey73/azure-cost-optimizer.git
   cd azure-cost-optimizer
   ```

2. **Set up a Python virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Authentication**:
   - Set up environment variables for Azure authentication:
     ```bash
     # Service Principal authentication
     export AZURE_TENANT_ID="your-tenant-id"
     export AZURE_CLIENT_ID="your-client-id"
     export AZURE_CLIENT_SECRET="your-client-secret"
     export AZURE_SUBSCRIPTION_ID="your-subscription-id"
     
     # Optional: Log Analytics
     export LOG_ANALYTICS_WORKSPACE_ID="your-workspace-id"
     ```
   - Or use Azure Key Vault for secure credential storage:
     ```bash
     export AZURE_KEY_VAULT_URL="https://your-keyvault.vault.azure.net/"
     ```

### Infrastructure Deployment

1. **Initialize Terraform**:
   ```bash
   cd infra
   terraform init
   ```

2. **Configure Terraform variables**:
   Create a `terraform.tfvars` file with:
   ```hcl
   subscription_id = "your-subscription-id"
   storage_account_name = "costoptimizer12345"  # Must be globally unique
   allowed_ip_ranges = ["123.123.123.123"]  # Your IP address
   ```

3. **Deploy infrastructure**:
   ```bash
   terraform plan -out=tfplan
   terraform apply tfplan
   ```

### Running the Optimizer

Execute the optimizer to generate cost optimization recommendations:

```bash
python src/optimizer.py --subscription-id "your-subscription-id" --start-date "2025-05-01" --end-date "2025-05-28"
```

See `docs/usage.md` for detailed command options and scenarios.

## Output

The optimizer generates a JSON file containing recommendations for:
- Idle VMs that could be shut down
- VMs that could be resized to smaller SKUs
- Orphaned disks that can be removed
- Cost anomalies that should be investigated

Example output:
```json
{
  "timestamp": "2025-05-28T14:30:00.000Z",
  "idleVMs": [
    {"resourceId": "/subscriptions/.../vm1", "averageCpu": 2.5}
  ],
  "skuResizes": [
    {"resourceId": "/subscriptions/.../vm2", "currentSku": "Standard_D8s_v3", "suggestedSku": "Standard_D4s_v3"}
  ],
  "orphanedDisks": [
    {"diskName": "disk1", "ageDays": 45}
  ],
  "costAnomalies": [
    {"date": "2025-05-15", "cost": 150.0, "baseline": 100.0}
  ]
}
```

## Documentation

For more detailed information, please refer to the following documents:

- [Architecture Overview](docs/architecture.md) - Solution architecture and component descriptions
- [Detailed Usage Guide](docs/usage.md) - Comprehensive instructions and examples
- [API Reference](docs/api_reference.md) - Detailed reference for all classes and methods
- [Security Best Practices](docs/security.md) - Security guidelines for deployment
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute to this project


## Security Considerations

This application supports multiple authentication methods for Azure:

- Service Principal with Client Secret (stored securely in Key Vault)
- Managed Identity (recommended for production)
- DefaultAzureCredential (integrates with VS Code, Azure CLI, etc.)

For production use, we recommend:

- Use Key Vault for all secrets
- Enable diagnostic settings on all resources
- Implement resource locks to prevent accidental deletion
- Apply least-privilege permissions for service principals

## Contributing

Contributions are welcome! Please follow the guidelines in `CONTRIBUTING.md` (if available).

## License

This project is licensed under the MIT License.
# src/config.py

import os

class Config:
    """
    Configuration for Azure Cost Optimizer.
    Reads from environment variables with sensible defaults.
    Can also retrieve secrets from Azure Key Vault.
    """
    def __init__(self):
        # Azure
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        
        # Key Vault URL (optional)
        self.key_vault_url = os.getenv("AZURE_KEY_VAULT_URL")
        if self.key_vault_url:
            self.get_secrets_from_keyvault(self.key_vault_url)

        # Log Analytics
        self.log_analytics_workspace_id = os.getenv("LOG_ANALYTICS_WORKSPACE_ID")

        # Optimization thresholds
        self.cpu_threshold = float(os.getenv("CPU_THRESHOLD", 5))
        self.disk_age_threshold = int(os.getenv("DISK_AGE_THRESHOLD_DAYS", 30))
        self.anomaly_percentage = float(os.getenv("ANOMALY_PERCENTAGE_THRESHOLD", 50))

        # Date range overrides (optional)
        self.start_date = os.getenv("START_DATE")  # YYYY-MM-DD
        self.end_date = os.getenv("END_DATE")      # YYYY-MM-DD

        # Output
        self.output_path = os.getenv("OUTPUT_PATH", "artifacts/recommendations.json")

    def as_dict(self):
        """Return configuration as dict for logging or debugging."""
        return {
            "subscription_id": self.subscription_id,
            "log_analytics_workspace_id": self.log_analytics_workspace_id,
            "cpu_threshold": self.cpu_threshold,
            "disk_age_threshold": self.disk_age_threshold,
            "anomaly_percentage": self.anomaly_percentage,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "output_path": self.output_path,
            "key_vault_url": self.key_vault_url,
        }
        
    def get_secrets_from_keyvault(self, vault_url):
        """
        Get secrets from Azure Key Vault
        
        Args:
            vault_url: The URL of the Key Vault
            
        Returns:
            bool: True if secrets were retrieved successfully, False otherwise
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient
            
            logger.info(f"Retrieving secrets from Azure Key Vault: {vault_url}")
            credential = DefaultAzureCredential(logging_enable=True)
            secret_client = SecretClient(vault_url=vault_url, credential=credential)
            
            # Get secrets (only if not already set from environment)
            if not self.client_secret:
                self.client_secret = secret_client.get_secret("azure-client-secret").value
                logger.info("Retrieved Azure client secret from Key Vault")
                
            # Attempt to get Log Analytics workspace ID if not set
            if not self.log_analytics_workspace_id:
                try:
                    self.log_analytics_workspace_id = secret_client.get_secret("log-analytics-workspace-id").value
                    logger.info("Retrieved Log Analytics workspace ID from Key Vault")
                except:
                    # Not a critical error if this isn't available
                    logger.warning("Log Analytics workspace ID not found in Key Vault")
                    
            return True
        except Exception as e:
            logger.error(f"Error retrieving secrets from Key Vault: {e}", exc_info=True)
            return False

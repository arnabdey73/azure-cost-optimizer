# src/config.py

import os

class Config:
    """
    Configuration for Azure Cost Optimizer.
    Reads from environment variables with sensible defaults.
    """
    def __init__(self):
        # Azure
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")

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
        }

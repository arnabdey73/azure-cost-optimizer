# src/azure_client.py

import os
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient


def get_credential():
    """
    Acquire Azure credential. Uses environment variables for SP or defaults.
    - If AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET are set, uses ClientSecretCredential.
    - Otherwise falls back to DefaultAzureCredential (managed identity, VS Code auth, etc.).
    """
    client_id = os.getenv("AZURE_CLIENT_ID")
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    try:
        if client_id and tenant_id and client_secret:
            return ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
            )
        return DefaultAzureCredential(logging_enable=True)
    except Exception as e:
        print(f"Error obtaining Azure credential: {e}")
        raise


class AzureCostClient:
    def __init__(self, subscription_id=None):
        """
        Initialize the Cost Management client.
        If subscription_id is None, fetches the first subscription from the account.
        """
        credential = get_credential()
        self.sub_client = SubscriptionClient(credential)
        if subscription_id:
            self.subscription_id = subscription_id
        else:
            # pick the first subscription
            subs = list(self.sub_client.subscriptions.list())
            self.subscription_id = subs[0].subscription_id

        self.cost_client = CostManagementClient(
            credential=credential,
            subscription_id=self.subscription_id
        )

    def list_subscriptions(self):
        """Return a list of subscription IDs accessible by the credential."""
        return [sub.subscription_id for sub in self.sub_client.subscriptions.list()]

    def get_cost_by_resource(self, start_date, end_date, granularity="Daily"):
        """
        Query cost data by resource between start_date and end_date (YYYY-MM-DD).
        Returns the raw response for further processing.
        """
        scope = f"/subscriptions/{self.subscription_id}"
        query = {
            "type": "Usage",
            "timeframe": None,
            "timePeriod": {"from": start_date, "to": end_date},
            "dataset": {
                "granularity": granularity,
                "aggregation": {
                    "totalCost": {"name": "PreTaxCost", "function": "Sum"}
                },
                "grouping": [{"type": "Dimension", "name": "ResourceId"}]
            }
        }
        return self.cost_client.query.usage(scope=scope, parameters=query)

    def get_cost_by_tag(self, tag_name, start_date, end_date):
        """
        Query cost aggregated by a specific tag.
        """
        scope = f"/subscriptions/{self.subscription_id}"
        query = {
            "type": "Usage",
            "timePeriod": {"from": start_date, "to": end_date},
            "dataset": {
                "aggregation": {
                    "cost": {"name": "PreTaxCost", "function": "Sum"}
                },
                "grouping": [{"type": "TagKey", "name": tag_name}]
            }
        }
        return self.cost_client.query.usage(scope=scope, parameters=query)
        
    def query_log_analytics(self, query, workspace_id=None):
        """
        Execute a query against Log Analytics workspace
        
        Args:
            query: The KQL query string
            workspace_id: Optional workspace ID (defaults to config)
            
        Returns:
            List of result rows
        """
        from azure.monitor.query import LogsQueryClient
        from src.config import Config
        
        config = Config()
        workspace_id = workspace_id or config.log_analytics_workspace_id
        if not workspace_id:
            raise ValueError("Log Analytics workspace ID is required")
            
        logs_client = LogsQueryClient(credential=get_credential())
        
        response = logs_client.query_workspace(
            workspace_id=workspace_id,
            query=query,
            timespan=None  # Use query's time constraints
        )
        
        results = []
        if response and response.tables:
            for row in response.tables[0].rows:
                # Convert to dict with column names
                result = {col.name: val for col, val in zip(response.tables[0].columns, row)}
                results.append(result)
                
        return results
    
    def list_disks(self):
        """
        List all managed disks in the subscription with their attachment status
        """
        from azure.mgmt.compute import ComputeManagementClient
        from datetime import datetime, timezone
        
        compute_client = ComputeManagementClient(
            credential=get_credential(),
            subscription_id=self.subscription_id
        )
        
        disks = []
        now = datetime.now(timezone.utc)
        
        for disk in compute_client.disks.list():
            # Calculate age in days
            created_time = disk.time_created
            age_days = (now - created_time).days if created_time else 0
            
            disks.append({
                "id": disk.id,
                "name": disk.name,
                "attachedTo": disk.disk_state == "Attached",
                "age": age_days,
                "sizeGB": disk.disk_size_gb,
                "skuName": disk.sku.name if disk.sku else None
            })
        
        return disks
    
    def query_cost_management(self, query_string):
        """
        Execute a query against Cost Management API
        
        Args:
            query_string: The query description or template
            
        Returns:
            List of result rows
        """
        # This is a simplified implementation that parses the query string
        # and constructs the appropriate Cost Management API request
        
        from datetime import datetime, timedelta
        import re
        
        # Extract date range from query if present
        date_range_match = re.search(r"between \(datetime\((.+?)\) \.\. datetime\((.+?)\)\)", query_string)
        if date_range_match:
            start_date = date_range_match.group(1)
            end_date = date_range_match.group(2)
        else:
            # Default to last 30 days
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
        # Prepare the appropriate query based on the query string
        scope = f"/subscriptions/{self.subscription_id}"
        
        if "dailyCost" in query_string:
            # Daily cost anomaly detection query
            query = {
                "type": "Usage",
                "timeframe": "Custom",
                "timePeriod": {"from": start_date, "to": end_date},
                "dataset": {
                    "granularity": "Daily",
                    "aggregation": {
                        "totalCost": {"name": "PreTaxCost", "function": "Sum"}
                    }
                }
            }
            response = self.cost_client.query.usage(scope=scope, parameters=query)
            
            # Process results for anomaly detection
            if response and hasattr(response, 'rows'):
                daily_costs = []
                for row in response.rows:
                    daily_costs.append({
                        "TimeGenerated": row[0],  # Date
                        "dailyCost": float(row[1]),  # Cost value
                        "baseline": 0  # Will be calculated after
                    })
                
                # Calculate baseline as average
                if daily_costs:
                    baseline = sum(r["dailyCost"] for r in daily_costs) / len(daily_costs)
                    for r in daily_costs:
                        r["baseline"] = baseline
                        
                # Filter for anomalies (cost > 150% of baseline)
                return [r for r in daily_costs if r["dailyCost"] > r["baseline"] * 1.5]
            
            return []
        else:
            # Default to resource cost query
            query = {
                "type": "Usage",
                "timeframe": "Custom",
                "timePeriod": {"from": start_date, "to": end_date},
                "dataset": {
                    "granularity": "None",
                    "aggregation": {
                        "totalCost": {"name": "PreTaxCost", "function": "Sum"}
                    },
                    "grouping": [
                        {"type": "Dimension", "name": "ResourceId"},
                        {"type": "Dimension", "name": "ResourceType"}
                    ]
                }
            }
            response = self.cost_client.query.usage(scope=scope, parameters=query)
            
            # Process and return results
            results = []
            if response and hasattr(response, 'rows'):
                for row in response.rows:
                    # Analyze VM sizes from resource type
                    resource_id = row[0] if len(row) > 0 else ""
                    resource_type = row[1] if len(row) > 1 else ""
                    cost = float(row[2]) if len(row) > 2 else 0
                    
                    # Extract SKU from resource ID for VMs
                    sku = "Unknown"
                    if "Microsoft.Compute/virtualMachines" in resource_type:
                        # This is a simplified approach - in real implementation
                        # you would query the Compute API to get the actual VM size
                        sku_match = re.search(r"Standard_\w+", resource_id)
                        if sku_match:
                            sku = sku_match.group(0)
                    
                    results.append({
                        "ResourceId": resource_id,
                        "ResourceType": resource_type,
                        "Cost": cost,
                        "SKU": sku
                    })
                    
            return results

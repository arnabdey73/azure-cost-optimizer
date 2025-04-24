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

    if client_id and tenant_id and client_secret:
        return ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )
    return DefaultAzureCredential()


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

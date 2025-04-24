import os
import pytest
from src.azure_client import get_credential, AzureCostClient

def test_get_credential_default(monkeypatch):
    # Ensure no env vars => DefaultAzureCredential returned
    monkeypatch.delenv("AZURE_CLIENT_ID", raising=False)
    monkeypatch.delenv("AZURE_TENANT_ID", raising=False)
    monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)
    cred = get_credential()
    # DefaultAzureCredential has attribute 'get_token'
    assert hasattr(cred, "get_token")

def test_list_subscriptions(monkeypatch):
    # Mock credential and subscription client to return dummy list
    class DummySub:
        subscription_id = "sub-123"
    class DummyClient:
        def __init__(self, credential):
            pass
        @property
        def subscriptions(self):
            return self
        def list(self):
            return [DummySub()]
    monkeypatch.setattr("src.azure_client.SubscriptionClient", DummyClient)
    client = AzureCostClient()
    subs = client.list_subscriptions()
    assert subs == ["sub-123"]

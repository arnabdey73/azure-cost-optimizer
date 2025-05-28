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
    
def test_get_credential_with_error(monkeypatch):
    # Test error handling in credential acquisition
    def mock_default_azure_credential(*args, **kwargs):
        raise Exception("Authentication failed")
    
    monkeypatch.setattr("src.azure_client.DefaultAzureCredential", mock_default_azure_credential)
    
    # Should propagate the exception after logging it
    with pytest.raises(Exception) as excinfo:
        get_credential()
    assert "Authentication failed" in str(excinfo.value)

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
    
def test_query_log_analytics(monkeypatch):
    # Mock the LogsQueryClient to return mock data
    class MockResponse:
        @property
        def tables(self):
            # Mock column and row data
            class MockColumn:
                def __init__(self, name):
                    self.name = name
            
            class MockTable:
                @property
                def columns(self):
                    return [MockColumn("ResourceId"), MockColumn("Count")]
                
                @property
                def rows(self):
                    return [
                        ["/subscriptions/123/resourceGroups/test/vm1", 42],
                        ["/subscriptions/123/resourceGroups/test/vm2", 17]
                    ]
            
            return [MockTable()]
    
    class MockLogsClient:
        def __init__(self, credential):
            pass
            
        def query_workspace(self, workspace_id, query, timespan):
            return MockResponse()
    
    # Mock Config to return a workspace ID
    class MockConfig:
        def __init__(self):
            self.log_analytics_workspace_id = "workspace-123"
    
    # Apply mocks
    monkeypatch.setattr("src.config.Config", MockConfig)
    monkeypatch.setattr("azure.monitor.query.LogsQueryClient", MockLogsClient)
    monkeypatch.setattr("src.azure_client.get_credential", lambda: None)
    
    # Create client and test the function
    client = AzureCostClient()
    results = client.query_log_analytics("test query")
    
    # Verify results
    assert len(results) == 2
    assert results[0]["ResourceId"] == "/subscriptions/123/resourceGroups/test/vm1"
    assert results[0]["Count"] == 42
    assert results[1]["ResourceId"] == "/subscriptions/123/resourceGroups/test/vm2"
    assert results[1]["Count"] == 17
    
def test_list_disks(monkeypatch):
    from datetime import datetime, timezone, timedelta
    
    # Mock data for disks
    class MockDisk:
        def __init__(self, id_val, name, disk_state, created_days_ago, size_gb, sku_name):
            self.id = id_val
            self.name = name
            self.disk_state = disk_state
            self.time_created = datetime.now(timezone.utc) - timedelta(days=created_days_ago)
            self.disk_size_gb = size_gb
            
            class Sku:
                def __init__(self, name):
                    self.name = name
            
            self.sku = Sku(sku_name) if sku_name else None
    
    # Mock the Compute client
    class MockDisksOperation:
        def list(self):
            return [
                MockDisk("disk1", "disk1", "Attached", 10, 128, "Standard_LRS"),
                MockDisk("disk2", "disk2", "Unattached", 45, 256, "Premium_LRS"),
                MockDisk("disk3", "disk3", "Attached", 5, 512, None)
            ]
    
    class MockComputeClient:
        def __init__(self, credential, subscription_id):
            self.disks = MockDisksOperation()
    
    # Apply mocks
    monkeypatch.setattr("azure.mgmt.compute.ComputeManagementClient", MockComputeClient)
    monkeypatch.setattr("src.azure_client.get_credential", lambda: None)
    
    # Create client and test the function
    client = AzureCostClient(subscription_id="sub-123")
    disks = client.list_disks()
    
    # Verify results
    assert len(disks) == 3
    assert disks[0]["name"] == "disk1"
    assert disks[0]["attachedTo"] is True
    assert disks[0]["sizeGB"] == 128
    assert disks[0]["skuName"] == "Standard_LRS"
    
    assert disks[1]["name"] == "disk2"
    assert disks[1]["attachedTo"] is False  # Unattached
    assert disks[1]["age"] > 40  # Should be around 45 days
    assert disks[1]["sizeGB"] == 256

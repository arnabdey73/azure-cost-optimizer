import json
import os
import pytest
from datetime import datetime
from src.optimizer import main, detect_idle_vms, suggest_sku_resize, find_orphaned_disks, detect_cost_anomalies

def test_main_creates_output(tmp_path, monkeypatch):
    # Setup tmp output path
    output_file = tmp_path / "recs.json"
    monkeypatch.setenv("OUTPUT_PATH", str(output_file))
    # Monkeypatch functions to return empty lists
    monkeypatch.setattr("src.optimizer.detect_idle_vms", lambda *args, **kwargs: [])
    monkeypatch.setattr("src.optimizer.suggest_sku_resize", lambda *args, **kwargs: [])
    monkeypatch.setattr("src.optimizer.find_orphaned_disks", lambda *args, **kwargs: [])
    monkeypatch.setattr("src.optimizer.detect_cost_anomalies", lambda *args, **kwargs: [])

    # Run main
    main()

    # Check file created and valid JSON
    assert output_file.exists()
    data = json.loads(output_file.read_text())
    assert "idleVMs" in data
    assert isinstance(data["idleVMs"], list)
    
def test_detect_idle_vms(monkeypatch):
    # Mock the AzureCostClient
    class MockClient:
        def query_log_analytics(self, query):
            # Return mock data
            return [
                {"ResourceId": "/subscriptions/123/resourceGroups/test/providers/Microsoft.Compute/virtualMachines/vm1", "avgCpu": 2.5},
                {"ResourceId": "/subscriptions/123/resourceGroups/test/providers/Microsoft.Compute/virtualMachines/vm2", "avgCpu": 10.5}
            ]
    
    # Test function
    results = detect_idle_vms(MockClient(), "2023-01-01", "2023-01-07", cpu_threshold=5)
    
    # Should only return the VM with CPU < threshold (5)
    assert len(results) == 1
    assert results[0]["resourceId"].endswith("vm1")
    assert results[0]["averageCpu"] == 2.5
    
def test_suggest_sku_resize(monkeypatch):
    # Mock the AzureCostClient
    class MockClient:
        def query_cost_management(self, query):
            # Return mock data for 3 VMs
            return [
                {"ResourceId": "/subscriptions/123/resourceGroups/test/providers/Microsoft.Compute/virtualMachines/vm1", "SKU": "Standard_D4s_v3"},
                {"ResourceId": "/subscriptions/123/resourceGroups/test/providers/Microsoft.Compute/virtualMachines/vm2", "SKU": "Standard_D8s_v3"},
                {"ResourceId": "/subscriptions/123/resourceGroups/test/providers/Microsoft.Compute/virtualMachines/vm3", "SKU": "Standard_F8s_v2"}
            ]
    
    # Test function
    results = suggest_sku_resize(MockClient(), "2023-01-01", "2023-01-07")
    
    # All VMs should have resize suggestions
    assert len(results) == 3
    assert any(r["resourceId"].endswith("vm1") for r in results)
    assert any(r["resourceId"].endswith("vm2") for r in results)
    assert any(r["resourceId"].endswith("vm3") for r in results)
    
def test_find_orphaned_disks(monkeypatch):
    # Mock the AzureCostClient
    class MockClient:
        def list_disks(self):
            # Return mock data with attached and detached disks
            return [
                {"id": "disk1", "name": "disk1", "attachedTo": True, "age": 40, "sizeGB": 128},
                {"id": "disk2", "name": "disk2", "attachedTo": None, "age": 45, "sizeGB": 256}, # Orphaned and old
                {"id": "disk3", "name": "disk3", "attachedTo": None, "age": 15, "sizeGB": 512}  # Orphaned but not old enough
            ]
    
    # Test function with 30 day threshold
    results = find_orphaned_disks(MockClient(), older_than_days=30)
    
    # Should only find disk2 which is both orphaned and older than 30 days
    assert len(results) == 1
    assert results[0]["diskName"] == "disk2"
    
def test_detect_cost_anomalies(monkeypatch):
    # Mock the AzureCostClient
    class MockClient:
        def query_cost_management(self, query):
            # Return mock data
            mock_datetime = datetime.now().isoformat()
            return [
                {"TimeGenerated": mock_datetime, "dailyCost": 150.0, "baseline": 100.0},  # 50% increase
                {"TimeGenerated": mock_datetime, "dailyCost": 120.0, "baseline": 100.0}   # 20% increase
            ]
    
    # Test function
    results = detect_cost_anomalies(MockClient(), "2023-01-01", "2023-01-07")
    
    # Should get both anomalies
    assert len(results) == 2
    assert results[0]["cost"] == 150.0
    assert results[1]["cost"] == 120.0

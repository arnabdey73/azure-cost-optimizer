import json
import os
import pytest
from src.optimizer import main

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

# src/optimizer.py

import argparse
import json
import os
from datetime import datetime, timedelta

from src.azure_client import AzureCostClient

def parse_args():
    parser = argparse.ArgumentParser(description="Azure Cost Optimization")
    parser.add_argument(
        "--subscription-id",
        help="Azure Subscription ID (defaults to first accessible subscription)",
    )
    parser.add_argument(
        "--start-date",
        default=(datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"),
        help="Start date for cost analysis (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end-date",
        default=datetime.utcnow().strftime("%Y-%m-%d"),
        help="End date for cost analysis (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--output",
        default="artifacts/recommendations.json",
        help="Path to output JSON recommendations",
    )
    return parser.parse_args()

def detect_idle_vms(cost_client, start_date, end_date, cpu_threshold=5):
    """
    Query Log Analytics for VM CPU metrics and identify VMs with average CPU < cpu_threshold over the period.
    """
    query = f"""
    Perf
    | where TimeGenerated between (datetime({start_date}) .. datetime({end_date}))
    | where CounterName == "\\% Processor Time" and CounterValue < {cpu_threshold}
    | summarize avgCpu=avg(CounterValue) by ResourceId
    """
    results = cost_client.query_log_analytics(query)
    return [
        {"resourceId": row["ResourceId"], "averageCpu": row["avgCpu"]}
        for row in results
    ]

def suggest_sku_resize(cost_client, start_date, end_date):
    """
    Analyze cost by VM SKU and usage metrics to recommend downsizing underutilized SKUs.
    """
    query = f"""
    Usage
    | where TimeGenerated between (datetime({start_date}) .. datetime({end_date}))
    | summarize totalCost=sum(Cost) by ResourceId, SKU
    | where totalCost < threshold
    """
    results = cost_client.query_cost_management(query)
    return [
        {"resourceId": row["ResourceId"], "currentSku": row["SKU"], "suggestedSku": "Standard_DS1_v2"}
        for row in results
    ]

def find_orphaned_disks(cost_client, older_than_days=30):
    """
    List managed disks not attached to any VM and older than the threshold.
    """
    disks = cost_client.list_disks()
    return [
        {"diskName": disk["name"], "ageDays": disk["age"]}
        for disk in disks
        if disk["attachedTo"] is None and disk["age"] > older_than_days
    ]

def detect_cost_anomalies(cost_client, start_date, end_date):
    """
    Compare daily cost to baseline average and flag days with spikes > X%.
    """
    query = f"""
    Usage
    | where TimeGenerated between (datetime({start_date}) .. datetime({end_date}))
    | summarize dailyCost=sum(Cost) by bin(TimeGenerated, 1d)
    | extend baseline=avg(dailyCost)
    | where dailyCost > baseline * 1.5
    """
    results = cost_client.query_cost_management(query)
    return [
        {"date": row["TimeGenerated"], "cost": row["dailyCost"], "baseline": row["baseline"]}
        for row in results
    ]

def main():
    args = parse_args()
    client = AzureCostClient(subscription_id=args.subscription_id)

    recs = {
        "timestamp": datetime.utcnow().isoformat(),
        "idleVMs": detect_idle_vms(client, args.start_date, args.end_date),
        "skuResizes": suggest_sku_resize(client, args.start_date, args.end_date),
        "orphanedDisks": find_orphaned_disks(client),
        "costAnomalies": detect_cost_anomalies(client, args.start_date, args.end_date),
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(recs, f, indent=2)

    print(f"Recommendations written to {args.output}")

if __name__ == "__main__":
    main()

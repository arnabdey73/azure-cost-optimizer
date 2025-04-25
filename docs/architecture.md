# Architecture Overview

This document describes the architecture and key components of the Azure Cost Optimizer solution.

## Data Flow Diagram

```text
┌───────────────────────────┐        ┌────────────────────────┐
│ Azure Cost Management API │───▶───▶│ Log Analytics Workspace│
└───────────────────────────┘        └────────────────────────┘
           │                                      │
           ▼                                      ▼
┌───────────────────────────┐        ┌────────────────────────┐
│    Azure Storage Export   │        │   Terraform Infra as   │
│  (Cost Exports to Blob)   │        │   Code (budgets, logs) │
└───────────────────────────┘        └────────────────────────┘
           │                                      │
           ▼                                      ▼
      ┌────────────────────────────────────────────────┐
      │            Python Optimizer Service            │
      │  • Fetches cost and usage metrics              │
      │  • Runs optimization rules                     │
      │  • Generates recommendations                   │
      │  • (Optional) Creates DevOps work items        │
      └────────────────────────────────────────────────┘

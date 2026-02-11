# AWS Infrastructure Setup Guide

**Netflix Lakehouse End-to-End Data Pipeline**

This guide provides step-by-step instructions to set up the complete AWS infrastructure for the Netflix lakehouse analytics platform.

---

## Prerequisites

### Required Tools

- **AWS Account** with appropriate permissions
- **AWS CLI** (version 2.x or higher)
- **Python 3.12+** with uv and pip
- **Git** for version control
- **Text editor** (VS Code recommended)

### Required Knowledge

- Basic understanding of AWS services
- SQL query fundamentals
- Python programming
- Command line interface familiarity

---

## Architecture Overview

### Medallion Architecture (Lakehouse)
```
Raw CSV (Bronze)
   → AWS Glue ETL (PySpark)
   → Processed Data (Silver)
   → Athena SQL Transformations
   → Curated Data (Gold)
   → Streamlit Dashboards
```

### AWS Services Used
- **Amazon S3** – Data lake storage (Bronze, Silver, Gold)
- **AWS Glue** – ETL jobs, crawlers, workflows
- **AWS Glue Data Catalog** – Metadata management
- **Amazon Athena** – Serverless analytics
- **CloudWatch** – Monitoring & logs
- **IAM** – Access control & security

---

## S3 Setup

### ***Create one bucket with the following structure:***
```
s3://netflix-pipeline-<your-name>/
│
├── raw/              # Bronze layer
├── processed/        # Silver layer
├── curated/          # Gold layer
├── rejected/         # Invalid records
├── scripts/          # Glue ETL scripts
└── athena-results/   # Athena query outputs
```

---

## IAM Configuration

Create:

- Glue Service Role with:
  - AmazonS3FullAccess
  - AWSGlueServiceRole
  - AmazonAthenaFullAccess
  - CloudWatchLogsFullAccess

**Note:** For production, use least-privilege policies.

---

## Glue Databases

### ***Create 3 Glue databases:***

| Layer  | Database Name          |
| ------ | ---------------------- |
| Bronze | `netflix_raw_db`       |
| Silver | `netflix_processed_db` |
| Gold   | `netflix_curated_db`   |

---

## ETL Jobs

### Bronze → Silver

- Script: `raw_to_processed.py`

- Output: Parquet (Snappy)

- Partitioned by: `content_type`

- Handles:

  - Validation

  - Deduplication

  - Rejected records

  - Data quality scoring

### Silver → Gold

- Script: netflix_silver_to_gold_etl.py

- Generates analytics-ready tables:
  - `content_overview`
  - `genre_analysis`
  - `geographic_distribution`
  - `temporal_trends`
  - `rating_distribution`
  - `quality_scorecard`
  - `top_producers`

--- 

## Glue Crawlers

***Run crawlers after each layer:***

| Layer  | Crawler Target |
| ------ | -------------- |
| Bronze | `raw/`         |
| Silver | `processed/`   |
| Gold   | `curated/`     |

---

## Orchestration

- **A Glue Workflow orchestrates:**
  - Bronze crawler
  - Bronze → Silver ETL
  - Silver crawler
  - Silver → Gold ETL
  - Gold crawler
- **Supports:**
  - Manual execution
  - Scheduled runs
  - Dependency handling
- **Triggers:**
  - On-demand for initial run
  - Conditional for ETL and crawler sequencing

---

## Athena Setup
- ***Configure query results location:***
  ```bash
  # Set in AWS Console → Athena → Settings
  s3://netflix-pipeline-<your-name>/athena-results/
  ```
- Query curated Gold tables for analytics
- Partition-aware queries for cost optimization

---

## Streamlit Dashboards 

***Local Run***

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run streamlit_app/Home.py
```
Dashboard reads Gold layer tables via Athena.

---

## Validation Checklist
  - ✅ Data present in all S3 layers
  - ✅ Glue jobs completed successfully
  - ✅ Tables visible in Glue Data Catalog
  - ✅ Athena queries return results
  - ✅ Streamlit dashboard loads correctly

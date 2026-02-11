# Netflix Lakehouse Architecture

**Deep Dive into Architectural Decisions and Component Selection**

---

## Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  NETFLIX LAKEHOUSE ANALYTICS PLATFORM                   │
│                                                                         │
│                       (Medallion Architecture)                          │
└─────────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
     │  INGESTION   │       │  PROCESSING  │       │ CONSUMPTION  │
     │              │       │              │       │              │
     │   S3 Raw     │ ────▶│   AWS Glue   │ ────▶ │   Athena +   │
     │   Landing    │       │  PySpark ETL │       │  Streamlit   │
     └──────────────┘       └──────────────┘       └──────────────┘
            │                      │                      │
            │                      │                      │
        🥉 BRONZE              🥈 SILVER               🥇 GOLD
        Raw Zone              Curated Zone           Business Zone
       CSV Format         Parquet (Partitioned)   Parquet (Aggregated)
            │                      │                      │
            └──────────────────────┴──────────────────────┘
                                   │
                      ┌────────────▼────────────┐
                      │  AWS Glue Data Catalog  │
                      │   (Unified Metadata)    │
                      └─────────────────────────┘
```


### Component Stack

| Layer | Components | Purpose |
|-------|-----------|---------|
| **Storage** | Amazon S3 | Unlimited scalable object storage |
| **Catalog** | AWS Glue Data Catalog | Centralized schema repository |
| **Processing** | AWS Glue (PySpark) | Serverless distributed ETL |
| **Query** | Amazon Athena | Serverless interactive SQL |
| **Orchestration** | AWS Glue Workflows | Dependency management & scheduling |
| **Visualization** | Streamlit | Rapid dashboard prototyping |
| **Security** | IAM, S3 Bucket Policies | Access control & encryption |

---

## Why Athena over Redshift
### Decision Driver: workload + cost

### Athena Wins Because:
-Serverless → no clusters, no idle cost
-Pay per scan → `~$5/TB`, `<$1/month` for this dataset
-Perfect for Parquet on S3
-Glue-native integration

### Redshift Rejected Because:
- Always-on cost (`~$180+/month`)
- Overkill for `<100 GB` data
- bOperational overhead (VACUUM, scaling, WLM)

### Rule of Thumb Used

- `<1 TB` data + `<200` queries/day → Athena
- `1 TB` + constant dashboards → Redshift

✅ Result: Athena delivers `1–2s` queries at `~10x` lower cost

---

## Why Streamlit over QuickSight
### Decision Driver: flexibility + portfolio value

### Streamlit Advantages
- Pure Python (Pandas, ML, custom logic)
- Dashboards in Git (CI/CD friendly)
- Zero vendor lock-in
- Free for local demos

### QuickSight Limitations
- Drag-and-drop only
- Limited advanced analytics
- Paid authors + per-session pricing

**Verdict**
- Portfolio + advanced analytics → Streamlit
- Enterprise BI at scale → QuickSight (future option)

## Lakehouse Principles Applied
| Principle             | Implementation                |
| --------------------- | ----------------------------- |
| Open formats          | Parquet + Snappy              |
| Separation of compute | S3 + Athena                   |
| Unified metadata      | Glue Data Catalog             |
| Multi-workload        | BI + Analytics + ML ready     |
| Governance            | Schema enforcement in Silver  |
| Performance           | Partitioning + column pruning |


## Medallion Architecture
### 🥉 Bronze – Raw Truth
- CSV as-is from source
- Immutable audit layer
- Schema-on-read
- Used for replay & debugging

### 🥈 Silver – Trusted Data
- Parquet + Snappy
- Schema enforced
- Partitioned by content_type
- Data quality scoring (`0–1`)
- Feature engineering applied

### Performance Gain
- CSV → Parquet = `8x` faster queries
- Partition pruning = `~30%` less scan cost

### 🥇 Gold – Business Ready
- Pre-aggregated tables
- No joins required
- `<1 MB` per table
- Sub-second dashboard loads
- Gold Tables
  - content_overview
  - genre_analysis
  - geographic_distribution
  - temporal_trends
  - rating_distribution
  - quality_scorecard
  - top_producers

--- 

## Data Quality Framework

### ***Enforced at Silver Layer***

| Dimension     | How                                  |
| ------------- | ------------------------------------ |
| Completeness  | Weighted quality score               |
| Validity      | Required fields (`show_id`, `title`) |
| Consistency   | Standardized nulls & formats         |
| Deduplication | Primary key based                    |
| Auditability  | Rejected records stored separately   |

#### Results
- Rejection rate: `0.08%`
- High-quality records (`>0.8`): `~96%`

---

## Query Optimization Strategy
| Technique             | Impact                     |
| --------------------- | -------------------------- |
| Parquet (columnar)    | Read only required columns |
| Snappy compression    | ~70% size reduction        |
| Partitioning          | Partition pruning          |
| Gold pre-aggregation  | 5x faster dashboards       |
| SELECT column pruning | 80–90% less data scanned   |

## Cost Summary (Monthly)
| Component      | Cost             |
| -------------- | ---------------- |
| S3 Storage     | `$2.30`          |
| Glue ETL       |` ~$6 `           |
| Athena Queries | `<$0.01 `        |
| Streamlit EC2  | `~$7.50`         |
| **Total**      | **`~$18/month`** |

With Free Tier & optimizations → `~$10/month`

---

## Scalability Strategy
| Data Size     | Strategy                      |
| ------------- | ----------------------------- |
| <1M rows      | Current stack (Athena + Glue) |
| 1–10M         | Add date partitions           |
| 10M+          | EMR + Delta/Iceberg           |
| Hot analytics | Redshift Spectrum             |
| Streaming     | Kinesis → S3                  |

---

## Final Verdict
- **This architecture is:**
  - Cost-optimized
  - Serverless
  - Production-aligned
  - Interview-ready
  - Easily scalable
- **Perfect for:**
  - Portfolio projects
  - Analytics platforms
  - Modern lakehouse demonstrations

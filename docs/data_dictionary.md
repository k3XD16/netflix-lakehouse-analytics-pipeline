# Data Dictionary

**Netflix Lakehouse Data Pipeline - Complete Schema Reference**: This document is the definitive data dictionary for the Netflix lakehouse architecture. It defines schemas, data types, and column-level descriptions for all tables across the Bronze (raw), Silver (processed), and Gold (curated) layers.

---

***Architecture:*** Medallion (Bronze → Silver → Gold)

***Tech Stack:*** AWS S3, Glue (PySpark), Athena, Parquet

---

## 1. Overview

| Layer      | Database               | Purpose                    | Format  |
| ---------- | ---------------------- | -------------------------- | ------- |
| **Bronze** | `netflix_raw_db`       | Immutable raw ingestion    | CSV     |
| **Silver** | `netflix_processed_db` | Cleaned & enriched dataset | Parquet |
| **Gold**   | `netflix_curated_db`   | Business-ready aggregates  | Parquet |

### Naming Standards

- Databases: `netflix_<layer>_db`
- Tables: `netflix_<layer>_<name>`
- Columns: `snake_case`
- Partitions: Hive-style (`key=value`)

## 2. Bronze Layer - Raw Ingestion

### *Table: `netflix_bronze_raw`*

Purpose: Preserve original Netflix catalog data (no transformations)

- Location: `s3://netflix-pipeline-khasim-2026/raw/`
- Row Count: `~8,800`
- Retention: Indefinite (audit & reprocessing)

### Core Schema


| Column         | Type   | Description           |
| -------------- | ------ | --------------------- |
| `show_id`      | STRING | Primary identifier    |
| `type`         | STRING | Movie / TV Show       |
| `title`        | STRING | Content title         |
| `director`     | STRING | Director(s)           |
| `cast`         | STRING | Cast list             |
| `country`      | STRING | Country of origin     |
| `date_added`   | STRING | Added to Netflix      |
| `release_year` | STRING | Original release year |
| `rating`       | STRING | Content rating        |
| `duration`     | STRING | Runtime or seasons    |
| `listed_in`    | STRING | Genres                |
| `description`  | STRING | Synopsis              |

### Notes

- No validation
- Nulls preserved as-is
- Read-only access

---

## 3. Silver Layer (Processed)

### *Table: `netflix_silver_processed`*

Purpose: Cleaned, enriched, and quality-scored dataset for analytics

- Location: `s3://netflix-pipeline-khasim-2026/processed/`
- Format: Parquet (Snappy)
- Partitioned by: `content_type` (Movie/TV Show)
- Rejection rate: `0.08%` (stored in `netflix_silver_rejected`)

### Key Transformations

- Enforced NOT NULL: `show_id`, `title`
- Standardized nulls (`Unknown`, `UNRATED`)
- Parsed dates → `DATE`
- Derived duration metrics
- Deduplication on `show_id`

### Core Schema:

| Column          | Type   | Description     |
| --------------- | ------ | --------------- |
| `show_id`       | STRING | Primary key     |
| `content_type`  | STRING | Movie / TV Show |
| `title`         | STRING | Title           |
| `director`      | STRING | Standardized    |
| `cast_and_crew` | STRING | Standardized    |
| `country`       | STRING | Standardized    |
| `date_added`    | DATE   | Parsed date     |
| `release_year`  | INT    | Release year    |
| `rating`        | STRING | Normalized      |
| `genre`         | STRING | Genre list      |

### Derived Features

| Column               | Type    | Description              |
| -------------------- | ------- | ------------------------ |
| `added_year`         | INT     | Year added               |
| `added_month`        | INT     | Month added              |
| `content_age_years`  | INT     | Age since release        |
| `duration_value`     | INT     | Numeric duration         |
| `duration_unit`      | STRING  | Minutes / Seasons        |
| `primary_genre`      | STRING  | First genre              |
| `has_director`       | BOOLEAN | Completeness flag        |
| `is_recent`          | BOOLEAN | Added ≤ 5 years          |
| `data_quality_score` | DOUBLE  | Completeness score (0–1) |

---

## 4. Gold Layer (Curated)

### *Table: `netflix_gold_curated`*

Purpose: Pre-aggregated, business-ready tables for dashboards & reporting

- Location: `s3://netflix-pipeline-khasim-2026/curated/`
- Partitioning: None (small tables)

### Gold Tables Summary

| Table                     | Grain           | Business Use         |
| ------------------------- | --------------- | -------------------- |
| `content_overview`        | 1 row           | Executive KPIs       |
| `genre_analysis`          | Genre × Type    | Content strategy     |
| `geographic_distribution` | Country         | Regional planning    |
| `temporal_trends`         | Month × Type    | Growth & seasonality |
| `rating_distribution`     | Rating × Type   | Audience targeting   |
| `quality_scorecard`       | Quality tier    | Data health          |
| `top_producers`           | Director × Type | Partnership insights |

---

## 5. Data Quality Rules

| Rule                | Action              |
| ------------------- | ------------------- |
| `show_id` NULL      | Reject              |
| `title` NULL        | Reject              |
| Duplicate `show_id` | Keep first          |
| Invalid dates       | Coalesce formats    |
| Missing attributes  | Standardized values |


### Silver Layer Metrics

- Avg quality score: **0.92**
- Records ≥ 0.8 score: **95%+**
- Rejection rate: **< 0.1%**

---

## 6. Partitioning Strategy

- Silver Layer

    - Partition Key: content_type
    - Reason: Low cardinality, high query filtering
    - Benefit: ~25–30% Athena scan reduction

- Gold Layer

    - No partitions (pre-aggregated, <1 MB each)

---

## 7. Change Log

### v1.0 (Feb 2026)

- Bronze, Silver, Gold layers implemented
- Data quality scoring introduced
- 7 curated analytical tables delivered
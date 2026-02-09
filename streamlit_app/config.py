"""
Netflix Analytics Pipeline - Configuration
"""
import os
from pathlib import Path

# AWS Configuration
AWS_REGION = "ap-south-1"
S3_BUCKET = "netflix-pipeline-khasim-2026"

# S3 Paths
S3_RAW_PATH = f"s3://{S3_BUCKET}/raw/"
S3_PROCESSED_PATH = f"s3://{S3_BUCKET}/processed/"
S3_CURATED_PATH = f"s3://{S3_BUCKET}/curated/"

# Glue Database Names
GLUE_RAW_DB = "netflix_raw_db"
GLUE_PROCESSED_DB = "netflix_processed_db"
GLUE_CURATED_DB = "netflix_curated_db"

# Glue Table Names
TABLE_RAW = f"{GLUE_RAW_DB}.raw"
TABLE_SILVER = f"{GLUE_PROCESSED_DB}.netflix_silver_processed"

# Gold Layer Tables
TABLE_CONTENT_OVERVIEW = f"{GLUE_CURATED_DB}.netflix_gold_content_overview"
TABLE_GENRE_ANALYSIS = f"{GLUE_CURATED_DB}.netflix_gold_genre_analysis"
TABLE_GEOGRAPHIC = f"{GLUE_CURATED_DB}.netflix_gold_geographic_distribution"
TABLE_RATING = f"{GLUE_CURATED_DB}.netflix_gold_rating_distribution"
TABLE_TEMPORAL = f"{GLUE_CURATED_DB}.netflix_gold_temporal_trends"
TABLE_QUALITY = f"{GLUE_CURATED_DB}.netflix_gold_quality_scorecard"
TABLE_PRODUCERS = f"{GLUE_CURATED_DB}.netflix_gold_top_producers"

# Athena Configuration
ATHENA_OUTPUT_LOCATION = f"s3://{S3_BUCKET}/athena_results/"

# Local Cache Configuration
LOCAL_DATA_DIR = Path(__file__).parent.parent / "data" / "curated"
CACHE_ENABLED = True

# Streamlit Configuration
PAGE_TITLE = "Netflix Lakehouse Analytics"
PAGE_ICON = "🎬"
LAYOUT = "wide"

# Visualization Settings
PLOTLY_THEME = "plotly_white"
COLOR_PALETTE = [
    "#d81f26",  # Netflix Red
    "#F6C81E",  # Netflix Black
    "#F5F5F1",  # Netflix White
    "#B20710",  # Dark Red
    "#831010",  # Darker Red
]
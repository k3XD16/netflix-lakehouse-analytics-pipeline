import pandas as pd
import numpy as np
import re
from datetime import datetime
import os

# --- CONFIGURATION ---
# Update these paths for your local machine
RAW_PATH = "data/raw/netflix_titles.csv"
PROCESSED_PATH = "data/processed/"

# Define strict valid ratings (Mirroring the Glue Job)
VALID_RATINGS = [
    "TV-MA", "TV-14", "TV-PG", "R", "PG-13", "TV-Y7", "TV-Y", "PG", "G", 
    "NC-17", "NR", "TV-G", "TV-Y7-FV", "UR", "UNRATED"
]

def clean_and_process_data(input_file, output_folder):
    print(f"📖 Reading raw data from: {input_file}")
    
    # 1. READ DATA
    # keep_default_na=False prevents pandas from auto-converting "" to NaN, 
    # but usually we want NaN to handle nulls easily.
    df = pd.read_csv(input_file)

    # 2. RENAME COLUMNS
    df = df.rename(columns={
        "type": "content_type",
        "listed_in": "genre",
        "cast": "cast_and_crew"
    })

    # 3. DEDUP & BASIC FILTER
    # Drop duplicates on show_id
    df = df.drop_duplicates(subset=["show_id"])
    # Drop rows where show_id or title is completely missing
    df = df.dropna(subset=["show_id", "title"])

    print(f"   ...Rows after dedup: {len(df)}")

    # 4. DATA CLEANING (The "Production Grade" Logic)

    # --- Handling Text Nulls (Fill with Defaults) ---
    # We use fillna() to handle NaNs and replace() to handle empty strings ""
    text_cols = {
        "director": "Unknown",
        "cast_and_crew": "Not Available",
        "country": "Unknown",
        "genre": "Uncategorized",
        "description": "No Description Available"
    }
    
    for col, default_val in text_cols.items():
        df[col] = df[col].fillna(default_val).replace("", default_val)

    # --- Rating Cleaning (The "Garbage" Filter) ---
    # Trim whitespace
    df["rating"] = df["rating"].astype(str).str.strip()
    
    # Apply the Allow-List Logic
    # If rating is NOT in VALID_RATINGS, force it to "UR"
    df["rating"] = df["rating"].apply(lambda x: x if x in VALID_RATINGS else "UR")

    # --- Date Parsing (date_added) ---
    # PySpark: to_date(..., "MMMM d, yyyy")
    # Pandas: to_datetime(..., format="%B %d, %Y")
    # errors='coerce' turns unparseable dates into NaT (Not a Time)
    df["date_added_parsed"] = pd.to_datetime(df["date_added"].str.strip(), format="%B %d, %Y", errors='coerce')
    
    # Fill NaT with Sentinel Value '1900-01-01'
    df["date_added"] = df["date_added_parsed"].fillna(pd.Timestamp("1900-01-01")).dt.date

    # --- Numeric Cleaning (release_year) ---
    # Fill NaN with 0, convert to integer
    df["release_year"] = pd.to_numeric(df["release_year"], errors='coerce').fillna(0).astype(int)

    # --- Duration Parsing (Regex Extraction) ---
    # Extract digits from string "90 min" -> 90
    df["duration_value"] = df["duration"].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)

    # --- Duration Unit Logic ---
    # numpy.select is like PySpark's when().otherwise()
    conditions = [
        df["duration"].astype(str).str.contains("min", case=False, na=False),
        df["duration"].astype(str).str.contains("Season", case=False, na=False)
    ]
    choices = ["minutes", "seasons"]
    df["duration_unit"] = np.select(conditions, choices, default="unknown")

    # --- Metadata Columns ---
    df["description_length"] = df["description"].str.len()
    df["processing_date"] = datetime.now().date()
    df["processed_timestamp"] = datetime.now()

    # Drop temporary columns
    df = df.drop(columns=["date_added_parsed"])

    # 5. WRITE TO PARQUET (Partitioned)
    # Ensure output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    print(f"💾 Writing processed data to: {output_folder}")
    
    # Requires 'pyarrow' or 'fastparquet' installed
    # partition_cols=['content_type'] creates the folder structure (content_type=Movie/...)
    df.to_parquet(
        output_folder, 
        partition_cols=["content_type"], 
        compression="snappy", 
        index=False
    )
    
    print("✅ Success! Local ETL Complete.")

# --- RUN IT ---
if __name__ == "__main__":
    clean_and_process_data(RAW_PATH, PROCESSED_PATH)
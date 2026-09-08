"""
MarketIq - Data Processor
--------------------------
Takes raw stock data (as fetched by the data fetcher) and cleans/structures
it into a usable format for downstream trend analysis.

Responsibilities:
- Load raw fetched data (CSV/JSON)
- Handle missing values and inconsistent date formats
- Normalize column names and types
- Save a cleaned, structured dataset for the next pipeline stage
"""

import pandas as pd
import os
from datetime import datetime


RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"


def load_raw_data(filepath: str) -> pd.DataFrame:
    """Load raw stock data from CSV or JSON into a DataFrame."""
    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath)
    elif filepath.endswith(".json"):
        df = pd.read_json(filepath)
    else:
        raise ValueError(f"Unsupported file type: {filepath}")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize raw stock data."""
    df = df.copy()

    # Normalize column names: lowercase, no spaces
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Drop fully empty rows
    df = df.dropna(how="all")

    # Standardize date column if present
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df = df.sort_values("date")

    # Fill missing numeric values using forward-fill, then back-fill as a fallback
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    df[numeric_cols] = df[numeric_cols].ffill().bfill()

    # Drop exact duplicate rows
    df = df.drop_duplicates()

    df = df.reset_index(drop=True)
    return df


def save_processed_data(df: pd.DataFrame, symbol: str) -> str:
    """Save cleaned data to the processed data directory."""
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d")
    out_path = os.path.join(PROCESSED_DATA_DIR, f"{symbol}_{timestamp}_processed.csv")
    df.to_csv(out_path, index=False)
    return out_path


def process_stock_file(filepath: str, symbol: str) -> str:
    """Full pipeline: load -> clean -> save. Returns path to processed file."""
    raw_df = load_raw_data(filepath)
    clean_df = clean_data(raw_df)
    out_path = save_processed_data(clean_df, symbol)
    print(f"[MarketIq] Processed {symbol}: {len(clean_df)} rows -> {out_path}")
    return out_path


if __name__ == "__main__":
    # Example usage — adjust filepath/symbol to match your fetcher's output
    example_file = os.path.join(RAW_DATA_DIR, "sample_stock_data.csv")
    if os.path.exists(example_file):
        process_stock_file(example_file, symbol="SAMPLE")
    else:
        print(f"[MarketIq] No sample file found at {example_file}. "
              f"Run the data fetcher first, or update RAW_DATA_DIR.")
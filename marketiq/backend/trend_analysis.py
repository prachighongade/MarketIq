"""
MarketIq - Trend Analyzer
--------------------------
Takes cleaned/processed stock data (output of data_processor.py) and scores
each stock on demand/momentum, so the system can flag which stocks are
trending up, trending down, or flat.

Metrics used (kept simple and explainable on purpose):
- pct_change: overall % price movement over the window
- momentum_score: short-term average change vs long-term average change
- volume_spike: how far recent volume deviates from its average
- demand_score: weighted combination of the above -> single ranking number

Expected input columns (from data_processor.py output):
- date, close (or 'close_price'), volume
Adjust COLUMN MAP below if your processed CSV uses different names.
"""

import pandas as pd
import os
import glob


PROCESSED_DATA_DIR = "data/processed"
ANALYSIS_OUTPUT_DIR = "data/analysis"

# Map your actual column names here if they differ
COLUMN_MAP = {
    "close": "close",
    "volume": "volume",
    "date": "date",
}

SHORT_WINDOW = 5   # days, for short-term momentum
LONG_WINDOW = 20    # days, for long-term momentum


def load_processed_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=[COLUMN_MAP["date"]])
    df = df.sort_values(COLUMN_MAP["date"]).reset_index(drop=True)
    return df


def compute_pct_change(df: pd.DataFrame) -> float:
    """Overall % change in closing price across the full window."""
    close_col = COLUMN_MAP["close"]
    if len(df) < 2:
        return 0.0
    start, end = df[close_col].iloc[0], df[close_col].iloc[-1]
    if start == 0:
        return 0.0
    return round(((end - start) / start) * 100, 2)


def compute_momentum_score(df: pd.DataFrame) -> float:
    """Compares short-term average daily change to long-term average daily change.
    Positive = accelerating upward, negative = losing steam or falling."""
    close_col = COLUMN_MAP["close"]
    daily_change = df[close_col].pct_change().fillna(0)

    short_avg = daily_change.tail(SHORT_WINDOW).mean()
    long_avg = daily_change.tail(LONG_WINDOW).mean()

    if long_avg == 0:
        return 0.0
    return round(((short_avg - long_avg) / abs(long_avg)) * 100, 2)


def compute_volume_spike(df: pd.DataFrame) -> float:
    """How far recent avg volume deviates from the longer-term avg volume."""
    vol_col = COLUMN_MAP["volume"]
    if vol_col not in df.columns:
        return 0.0

    recent_avg = df[vol_col].tail(SHORT_WINDOW).mean()
    baseline_avg = df[vol_col].tail(LONG_WINDOW).mean()

    if baseline_avg == 0:
        return 0.0
    return round(((recent_avg - baseline_avg) / baseline_avg) * 100, 2)


def compute_demand_score(pct_change: float, momentum: float, volume_spike: float) -> float:
    """Single weighted score to rank stocks by overall 'demand'.
    Weights are a starting point -- tune once you see real output."""
    weights = {"pct_change": 0.4, "momentum": 0.4, "volume_spike": 0.2}
    score = (
        pct_change * weights["pct_change"]
        + momentum * weights["momentum"]
        + volume_spike * weights["volume_spike"]
    )
    return round(score, 2)


def analyze_stock(filepath: str, symbol: str) -> dict:
    """Run full analysis on one processed stock file. Returns a result dict."""
    df = load_processed_data(filepath)

    pct_change = compute_pct_change(df)
    momentum = compute_momentum_score(df)
    volume_spike = compute_volume_spike(df)
    demand_score = compute_demand_score(pct_change, momentum, volume_spike)

    return {
        "symbol": symbol,
        "pct_change": pct_change,
        "momentum_score": momentum,
        "volume_spike": volume_spike,
        "demand_score": demand_score,
    }


def analyze_all(processed_dir: str = PROCESSED_DATA_DIR) -> pd.DataFrame:
    """Run analysis on every processed file and return a ranked DataFrame."""
    results = []
    for filepath in glob.glob(os.path.join(processed_dir, "*_processed.csv")):
        symbol = os.path.basename(filepath).split("_")[0]
        try:
            results.append(analyze_stock(filepath, symbol))
        except Exception as e:
            print(f"[MarketIq] Skipped {symbol}: {e}")

    result_df = pd.DataFrame(results)
    if not result_df.empty:
        result_df = result_df.sort_values("demand_score", ascending=False).reset_index(drop=True)

    return result_df


def save_analysis(result_df: pd.DataFrame) -> str:
    os.makedirs(ANALYSIS_OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(ANALYSIS_OUTPUT_DIR, "demand_ranking.csv")
    result_df.to_csv(out_path, index=False)
    return out_path


if __name__ == "__main__":
    ranking = analyze_all()
    if ranking.empty:
        print(f"[MarketIq] No processed files found in {PROCESSED_DATA_DIR}. "
              f"Run data_processor.py first.")
    else:
        out_path = save_analysis(ranking)
        print(f"[MarketIq] Ranked {len(ranking)} stocks by demand -> {out_path}")
        print(ranking.to_string(index=False))
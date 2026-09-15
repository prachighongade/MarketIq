"""
MarketIq - Data Fetcher
--------------------------
Fetches raw stock data from Yahoo Finance (via yfinance) and saves it into
data/raw/ in the exact format data_processor.py expects:
    symbol, date, close, volume

Usage:
    python data_fetcher.py
    (edit SYMBOLS list below, or import fetch_symbol() elsewhere)
"""

import yfinance as yf
import pandas as pd
import os

from db import save_price_data

RAW_DATA_DIR = "data/raw"

# Yahoo Finance tickers for NSE stocks use a ".NS" suffix.
# Add/remove symbols here as needed.
SYMBOLS = [
    "TCS.NS",
    "RELIANCE.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
]

PERIOD = "3mo"     # how far back to fetch
INTERVAL = "1d"    # daily candles


def fetch_symbol(ticker: str, period: str = PERIOD, interval: str = INTERVAL) -> pd.DataFrame:
    """Fetch raw OHLCV data for one ticker and reshape into the required columns."""
    data = yf.Ticker(ticker).history(period=period, interval=interval)

    if data.empty:
        raise ValueError(f"No data returned for {ticker}")

    data = data.reset_index()

    # Reshape into the exact columns data_processor.py requires
    df = pd.DataFrame({
        "symbol": ticker.replace(".NS", ""),
        "date": data["Date"],
        "close": data["Close"],
        "volume": data["Volume"],
    })

    return df


def save_raw_data(df: pd.DataFrame, symbol: str) -> str:
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    out_path = os.path.join(RAW_DATA_DIR, f"{symbol}.csv")
    df.to_csv(out_path, index=False)
    return out_path


def fetch_all(symbols=SYMBOLS):
    """Fetch and save raw data for every symbol in the list."""
    saved = []
    for ticker in symbols:
        symbol = ticker.replace(".NS", "")
        try:
            df = fetch_symbol(ticker)
            out_path = save_raw_data(df, symbol)
            print(f"[MarketIq] Fetched {symbol}: {len(df)} rows -> {out_path}")
            saved.append(out_path)

            db_rows = save_price_data(df)
            print(f"[MarketIq] Persisted {symbol}: {db_rows} rows -> TimescaleDB")
        except Exception as e:
            print(f"[MarketIq] Failed to fetch {ticker}: {e}")
    return saved


if __name__ == "__main__":
    fetch_all()
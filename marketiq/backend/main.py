"""
MarketIq - API Layer
--------------------------
Exposes the existing pipeline (data_processor.py -> trend_analysis.py)
as HTTP endpoints so the frontend / scheduler / anything else can call it.
"""
from db import get_latest_demand_rankings 
from fastapi import FastAPI, HTTPException
import os
import glob

from data_processor import process_stock_file, PROCESSED_DATA_DIR
from trend_analysis import analyze_stock, analyze_all, save_analysis
 
app = FastAPI(title="MarketIq API")
 
 
@app.get("/")
def root():
    return {"status": "MarketIq backend running"}
 
 
@app.post("/process")
def process_stock(filepath: str, symbol: str):
    """
    Run the raw -> processed pipeline for one stock file.
    Example: POST /process?filepath=data/raw/TCS.csv&symbol=TCS
    """
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File not found: {filepath}")
    try:
        out_path = process_stock_file(filepath, symbol)
        return {"symbol": symbol, "processed_file": out_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@app.get("/analysis/{symbol}")
def get_symbol_analysis(symbol: str):
    """
    Analyze the most recent processed file for a given symbol.
    Looks for files matching '{symbol}_*_processed.csv' in data/processed.
    """
    matches = glob.glob(os.path.join(PROCESSED_DATA_DIR, f"{symbol}_*_processed.csv"))
    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"No processed data found for {symbol}. Run /process first."
        )
    latest_file = max(matches, key=os.path.getmtime)
    try:
        result = analyze_stock(latest_file, symbol)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@app.get("/analysis")
def get_ranking():
    """
    Run analysis on every processed file and return stocks ranked by demand_score.
    """
    ranking_df = analyze_all()
    if ranking_df.empty:
        raise HTTPException(
            status_code=404,
            detail="No processed files found. Run /process for some symbols first."
        )
    save_analysis(ranking_df)
    return ranking_df.to_dict(orient="records")

@app.get("/rankings")
def get_rankings(limit: int = 10):
    try:
        rankings = get_latest_demand_rankings(limit=limit)  # query from db.py
        return {"rankings": rankings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
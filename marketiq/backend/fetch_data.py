import yfinance as yf

def fetch_stock_data(ticker="RELIANCE.NS", period="5d"):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data

if __name__ == "__main__":
    df = fetch_stock_data()
    print(df)
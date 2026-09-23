import logging
import yfinance as yf

logger = logging.getLogger(__name__)

BENCHMARK_SYMBOL = "^NSEI"  # Nifty 50 index


def get_benchmark_momentum(short_window=5, long_window=20, period="3mo"):
    """Momentum of the Nifty 50 index, computed as the spread between
    short and long average daily returns, in percentage points."""
    data = yf.download(
        BENCHMARK_SYMBOL, period=period, auto_adjust=True, progress=False
    )
    if data is None or data.empty:
        raise ValueError("No benchmark data returned for " + BENCHMARK_SYMBOL)

    close = data["Close"]
    if hasattr(close, "columns"):  # newer yfinance returns a 1-column DataFrame
        close = close.squeeze()

    returns = close.pct_change().dropna()
    if len(returns) < long_window:
        raise ValueError("Not enough benchmark history for the long window")

    short_avg = returns.tail(short_window).mean()
    long_avg = returns.tail(long_window).mean()
    momentum = float((short_avg - long_avg) * 100)
    logger.info("Benchmark momentum (%s): %.4f", BENCHMARK_SYMBOL, momentum)
    return momentum


def relative_strength(stock_momentum, benchmark_momentum):
    """How much a stock's momentum beats (or lags) the market."""
    return stock_momentum - benchmark_momentum


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Nifty 50 momentum:", get_benchmark_momentum())
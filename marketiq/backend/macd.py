"""MACD (Moving Average Convergence Divergence) indicator."""

from __future__ import annotations

import pandas as pd

_EPS = 1e-9


def compute_macd(close, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Return a DataFrame with macd, signal and histogram columns.

    macd      = EMA(fast) - EMA(slow)
    signal    = EMA(macd, signal)
    histogram = macd - signal
    """
    if min(fast, slow, signal) < 1:
        raise ValueError("fast, slow and signal periods must be >= 1")
    if fast >= slow:
        raise ValueError("fast period must be smaller than slow period")

    prices = pd.Series(close, dtype="float64").reset_index(drop=True)

    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()

    return pd.DataFrame(
        {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": macd_line - signal_line,
        }
    )


def macd_signal(close, fast: int = 12, slow: int = 26, signal: int = 9) -> str:
    """Classify the latest MACD state.

    Returns one of: bullish_crossover, bearish_crossover, bullish,
    bearish, neutral.
    """
    frame = compute_macd(close, fast, slow, signal)
    if len(frame) < 2:
        return "neutral"

    prev = _clean(frame["histogram"].iloc[-2])
    curr = _clean(frame["histogram"].iloc[-1])

    if prev <= 0 < curr:
        return "bullish_crossover"
    if prev >= 0 > curr:
        return "bearish_crossover"
    if curr > 0:
        return "bullish"
    if curr < 0:
        return "bearish"
    return "neutral"


def _clean(value: float) -> float:
    """Treat floating-point noise as zero."""
    return 0.0 if abs(value) < _EPS else float(value)
"""Technical indicators for stock trend analysis."""
from __future__ import annotations

from typing import Optional, Sequence

Series = list[Optional[float]]


def _check_window(window: int) -> None:
    if window <= 0:
        raise ValueError("window must be a positive integer")


def sma(prices: Sequence[float], window: int) -> Series:
    """Simple moving average. First window-1 values are None."""
    _check_window(window)
    out: Series = [None] * len(prices)
    if len(prices) < window:
        return out
    running = sum(prices[:window])
    out[window - 1] = running / window
    for i in range(window, len(prices)):
        running += prices[i] - prices[i - window]
        out[i] = running / window
    return out


def ema(prices: Sequence[float], window: int) -> Series:
    """Exponential moving average, seeded with the SMA of the first window."""
    _check_window(window)
    out: Series = [None] * len(prices)
    if len(prices) < window:
        return out
    alpha = 2 / (window + 1)
    prev = sum(prices[:window]) / window
    out[window - 1] = prev
    for i in range(window, len(prices)):
        prev = alpha * prices[i] + (1 - alpha) * prev
        out[i] = prev
    return out


def _rsi_value(avg_gain: float, avg_loss: float) -> float:
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


def rsi(prices: Sequence[float], period: int = 14) -> Series:
    """Relative Strength Index using Wilder's smoothing."""
    _check_window(period)
    out: Series = [None] * len(prices)
    if len(prices) <= period:
        return out

    gains, losses = [], []
    for i in range(1, period + 1):
        change = prices[i] - prices[i - 1]
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    out[period] = _rsi_value(avg_gain, avg_loss)

    for i in range(period + 1, len(prices)):
        change = prices[i] - prices[i - 1]
        avg_gain = (avg_gain * (period - 1) + max(change, 0.0)) / period
        avg_loss = (avg_loss * (period - 1) + max(-change, 0.0)) / period
        out[i] = _rsi_value(avg_gain, avg_loss)
    return out


def trend_signal(prices: Sequence[float], short: int = 5, long: int = 20) -> str:
    """Return 'bullish', 'bearish', 'neutral' or 'insufficient_data'."""
    if short >= long:
        raise ValueError("short window must be smaller than long window")
    if len(prices) < long:
        return "insufficient_data"
    short_ma = sma(prices, short)[-1]
    long_ma = sma(prices, long)[-1]
    if short_ma > long_ma:
        return "bullish"
    if short_ma < long_ma:
        return "bearish"
    return "neutral"
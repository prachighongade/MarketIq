"""Bollinger Bands volatility indicator."""
from statistics import pstdev


def bollinger_bands(prices, window=20, num_std=2.0):
    """Return upper, middle and lower bands, one value per full window."""
    if window < 2:
        raise ValueError("window must be at least 2")
    if len(prices) < window:
        raise ValueError("not enough prices for the given window")

    upper, middle, lower = [], [], []
    for i in range(window - 1, len(prices)):
        chunk = prices[i - window + 1 : i + 1]
        mean = sum(chunk) / window
        spread = num_std * pstdev(chunk)
        middle.append(mean)
        upper.append(mean + spread)
        lower.append(mean - spread)
    return {"upper": upper, "middle": middle, "lower": lower}


def percent_b(price, upper, lower):
    """Position of price within the bands: 0 = lower band, 1 = upper band."""
    if upper == lower:
        return 0.5
    return (price - lower) / (upper - lower)
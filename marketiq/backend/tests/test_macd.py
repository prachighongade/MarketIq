import pytest

from macd import compute_macd, macd_signal


def test_output_columns_and_length():
    prices = list(range(1, 61))
    result = compute_macd(prices)
    assert list(result.columns) == ["macd", "signal", "histogram"]
    assert len(result) == len(prices)


def test_constant_prices_give_zero_macd():
    result = compute_macd([100.0] * 50)
    assert result["macd"].abs().max() < 1e-9
    assert result["histogram"].abs().max() < 1e-9


def test_histogram_equals_macd_minus_signal():
    result = compute_macd([10, 12, 11, 15, 14, 18, 17, 21, 20, 25] * 4)
    diff = result["macd"] - result["signal"] - result["histogram"]
    assert diff.abs().max() < 1e-9


def test_rising_prices_are_bullish():
    assert macd_signal(list(range(1, 61))) == "bullish"


def test_falling_prices_are_bearish():
    assert macd_signal(list(range(60, 0, -1))) == "bearish"


def test_single_price_is_neutral():
    assert macd_signal([100.0]) == "neutral"


def test_bullish_crossover_detected_on_reversal():
    prices = list(range(100, 60, -1)) + list(range(60, 120, 3))
    signals = [macd_signal(prices[:i]) for i in range(2, len(prices) + 1)]
    assert "bullish_crossover" in signals


def test_bearish_crossover_detected_on_reversal():
    prices = list(range(60, 100, 1)) + list(range(100, 40, -3))
    signals = [macd_signal(prices[:i]) for i in range(2, len(prices) + 1)]
    assert "bearish_crossover" in signals


def test_fast_must_be_smaller_than_slow():
    with pytest.raises(ValueError):
        compute_macd([1, 2, 3], fast=26, slow=12)


def test_periods_must_be_positive():
    with pytest.raises(ValueError):
        compute_macd([1, 2, 3], fast=0)
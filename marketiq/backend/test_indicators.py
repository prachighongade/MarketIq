import pytest

from indicators import ema, rsi, sma, trend_signal


def test_sma_basic():
    assert sma([1, 2, 3, 4, 5], 3) == [None, None, 2, 3, 4]


def test_sma_short_input():
    assert sma([1, 2], 3) == [None, None]


def test_invalid_window():
    with pytest.raises(ValueError):
        sma([1, 2, 3], 0)


def test_ema_basic():
    result = ema([1, 2, 3, 4, 5], 3)
    assert result[:2] == [None, None]
    assert result[2:] == pytest.approx([2, 3, 4])


def test_rsi_all_gains_is_100():
    assert rsi([1, 2, 3, 4, 5], period=3)[-1] == 100.0


def test_rsi_all_losses_is_0():
    assert rsi([5, 4, 3, 2, 1], period=3)[-1] == 0.0


def test_rsi_not_enough_data():
    assert rsi([1, 2, 3], period=14) == [None, None, None]


def test_trend_bullish():
    assert trend_signal(list(range(1, 31))) == "bullish"


def test_trend_bearish():
    assert trend_signal(list(range(30, 0, -1))) == "bearish"


def test_trend_neutral():
    assert trend_signal([10] * 30) == "neutral"


def test_trend_insufficient_data():
    assert trend_signal([1, 2, 3]) == "insufficient_data"
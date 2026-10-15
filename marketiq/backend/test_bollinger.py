import pytest

from bollinger import bollinger_bands, percent_b


def test_constant_prices_have_zero_width():
    bands = bollinger_bands([10, 10, 10, 10, 10], window=5)
    assert bands["upper"] == bands["middle"] == bands["lower"] == [10]


def test_known_values():
    bands = bollinger_bands([1, 2, 3, 4, 5], window=5, num_std=2)
    assert bands["middle"][0] == pytest.approx(3)
    assert bands["upper"][0] == pytest.approx(3 + 2 * 2 ** 0.5)
    assert bands["lower"][0] == pytest.approx(3 - 2 * 2 ** 0.5)


def test_output_length():
    bands = bollinger_bands(list(range(1, 11)), window=4)
    assert len(bands["middle"]) == 7


def test_too_few_prices_raises():
    with pytest.raises(ValueError):
        bollinger_bands([1, 2, 3], window=5)


def test_percent_b():
    assert percent_b(5, upper=10, lower=0) == 0.5
    assert percent_b(7, upper=7, lower=7) == 0.5

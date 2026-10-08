from datetime import datetime

from market_hours import IST, is_market_open


def test_open_during_session():
    # Monday 11:00 IST
    assert is_market_open(datetime(2026, 10, 5, 11, 0, tzinfo=IST))


def test_closed_before_open():
    assert not is_market_open(datetime(2026, 10, 5, 9, 0, tzinfo=IST))


def test_closed_after_close():
    assert not is_market_open(datetime(2026, 10, 5, 15, 31, tzinfo=IST))


def test_closed_on_weekend():
    # Saturday 11:00 IST
    assert not is_market_open(datetime(2026, 10, 10, 11, 0, tzinfo=IST))
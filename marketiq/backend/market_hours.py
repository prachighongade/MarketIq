"""Helpers for checking whether the NSE equity market is open."""

from datetime import datetime, time, timedelta, timezone

# India has no daylight saving, so a fixed UTC+5:30 offset is safe.
IST = timezone(timedelta(hours=5, minutes=30))

MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)


def now_ist() -> datetime:
    """Current time in Indian Standard Time."""
    return datetime.now(IST)


def is_weekday(moment: datetime) -> bool:
    """True for Monday to Friday."""
    return moment.weekday() < 5


def is_market_open(moment: datetime | None = None) -> bool:
    """Return True if NSE regular trading hours are on at the given time.

    Regular session: Monday to Friday, 09:15 to 15:30 IST.
    Exchange holidays are not handled here.
    """
    moment = moment.astimezone(IST) if moment else now_ist()
    if not is_weekday(moment):
        return False
    return MARKET_OPEN <= moment.time() <= MARKET_CLOSE
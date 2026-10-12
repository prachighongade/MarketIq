"""Summarize commit activity from git history."""
import subprocess
import sys
from collections import Counter
from datetime import date, timedelta


def get_commit_dates():
    out = subprocess.run(
        ["git", "log", "--pretty=format:%ad", "--date=short"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def current_streak(counts):
    day = date.today()
    if counts.get(day.isoformat(), 0) == 0:
        day -= timedelta(days=1)
    streak = 0
    while counts.get(day.isoformat(), 0) > 0:
        streak += 1
        day -= timedelta(days=1)
    return streak


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    counts = Counter(get_commit_dates())
    print(f"Total commits: {sum(counts.values())}")
    print(f"Active days: {len(counts)}")
    print(f"Current streak: {current_streak(counts)} day(s)\n")
    for i in range(days - 1, -1, -1):
        d = (date.today() - timedelta(days=i)).isoformat()
        n = counts.get(d, 0)
        print(f"{d}  {'#' * n} {n}")


if __name__ == "__main__":
    main()
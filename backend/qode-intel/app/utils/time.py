from datetime import datetime, timedelta, timezone

# We treat storage in UTC, but compute 24h windows from Asia/Kolkata
IST = timezone(timedelta(hours=5, minutes=30))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def kst_now() -> datetime:
    # legacy name kept for compatibility; returns IST now
    return datetime.now(IST) + timedelta(minutes=10)


def last_24h_window():
    end_ist = kst_now()
    start_ist = end_ist - timedelta(hours=24)
    return start_ist.astimezone(timezone.utc), end_ist.astimezone(timezone.utc)

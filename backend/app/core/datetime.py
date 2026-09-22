from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Return the current UTC time as a naive datetime.

    The database currently uses SQLAlchemy DateTime columns
    without timezone=True, so we intentionally remove the
    timezone information while keeping the value in UTC.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
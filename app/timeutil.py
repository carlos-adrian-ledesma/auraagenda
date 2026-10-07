from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def system_timezone_name() -> str:
    local = datetime.now().astimezone().tzinfo
    key = getattr(local, "key", None)
    return key or str(local) or "UTC"


def now_in_timezone(name: str | None) -> datetime:
    if name:
        try:
            return datetime.now(ZoneInfo(name))
        except (ZoneInfoNotFoundError, ValueError):
            pass
    return datetime.now().astimezone()

from __future__ import annotations

from datetime import date, datetime, time

QT_TO_STRFTIME = {
    "dd/MM/yyyy": "%d/%m/%Y",
    "MM/dd/yyyy": "%m/%d/%Y",
    "yyyy-MM-dd": "%Y-%m-%d",
}


def _as_date(value: str | date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def _as_time(value: str | time | datetime) -> time:
    if isinstance(value, datetime):
        return value.time()
    if isinstance(value, time):
        return value
    text = str(value).strip()
    return time.fromisoformat(text[:8] if len(text) >= 8 else text)


def format_date(value: str | date | datetime, qt_format: str = "dd/MM/yyyy") -> str:
    try:
        return _as_date(value).strftime(QT_TO_STRFTIME.get(qt_format, "%d/%m/%Y"))
    except (ValueError, TypeError):
        return str(value or "")


def format_time(value: str | time | datetime, clock: str = "24") -> str:
    try:
        parsed = _as_time(value)
        return parsed.strftime("%I:%M %p" if str(clock) == "12" else "%H:%M")
    except (ValueError, TypeError):
        return str(value or "")


def format_datetime(value: str | datetime, qt_format: str = "dd/MM/yyyy", clock: str = "24") -> str:
    try:
        parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value))
        return f"{format_date(parsed, qt_format)} {format_time(parsed, clock)}"
    except (ValueError, TypeError):
        return str(value or "")


def format_number(value: float | int, language: str = "es") -> str:
    number = f"{float(value):,.2f}"
    if language == "es":
        return number.replace(",", "_").replace(".", ",").replace("_", ".")
    return number


def format_currency(value: float | int, currency: str, language: str = "es") -> str:
    code = (currency or "").strip().upper()
    return f"{code} {format_number(value, language)}".strip()

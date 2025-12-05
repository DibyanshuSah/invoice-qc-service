import re
from datetime import datetime, date
from typing import Optional

# -----------------------------
# Parse an amount string -> float
# -----------------------------
def parse_amount(value: str) -> Optional[float]:
    if not value:
        return None

    value = value.replace(",", "").replace(" ", "").strip()

    try:
        return float(value)
    except:
        return None


# -----------------------------
# Parse a date string -> ISO date
# -----------------------------
def parse_date(value: str) -> Optional[str]:
    if not value:
        return None

    value = value.strip()

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y-%m-%d",
        "%d/%m/%y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.date().isoformat()
        except:
            pass

    return None


# -----------------------------
# Today in ISO format
# -----------------------------
def today_iso():
    return date.today().isoformat()

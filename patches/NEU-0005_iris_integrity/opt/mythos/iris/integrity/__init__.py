"""
iris/integrity — Iris's immune system interface (NEU-0005)
Iris reads her own integrity state and carries it in awareness.
"""
from .iris_integrity import (
    run_integrity_scan,
    read_latest_integrity_report,
    build_health_summary,
    format_telegram_report,
    format_iris_context,
)

__all__ = [
    "run_integrity_scan",
    "read_latest_integrity_report",
    "build_health_summary",
    "format_telegram_report",
    "format_iris_context",
]

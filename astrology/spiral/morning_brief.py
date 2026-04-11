"""
SEN-0006: Spiral Time Walker — Morning Brief Assembler

Assembles the daily morning brief for Ka'tuar'el:
  - Current spiral position (Cycle.Day, name, tone, focus)
  - Transit pressure (exact, building, watch)
  - Delivered once per day on first Iris message

Iris delivers this as her opening before responding to whatever was said.
The brief is woven into her response — not a dump, a reading.
"""

import logging
import os
from datetime import date, datetime, timezone
from typing import Optional

import psycopg2
import psycopg2.extras

from .spiral_engine import get_position, SpiralPosition, SPIRAL_DAYS
from .transit_pressure import (
    run_daily_pressure, get_todays_pressure, format_pressure_brief
)
from .transit_interpreter import interpret_transits, format_pressure_brief_with_interp

log = logging.getLogger("iris.morning_brief")

# chart_id for Adge / Ka'tuar'el
ADGE_CHART_ID = 9
ADGE_PERSON_ID = "adge"


def _get_conn():
    db_url = f"postgresql://{os.environ.get('POSTGRES_USER', 'postgres')}@/mythos?host={os.environ.get('POSTGRES_HOST', '/var/run/postgresql')}"
    return psycopg2.connect(db_url)


# ── Delivery Tracking ─────────────────────────────────────────────────────────

def has_brief_been_delivered(person_id: str, brief_date: Optional[date] = None) -> bool:
    """Check if morning brief was already delivered today."""
    if brief_date is None:
        brief_date = date.today()
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT delivered FROM spiral_morning_brief_log
            WHERE person_id = %s AND brief_date = %s
        """, (person_id, brief_date))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return bool(row and row[0])
    except Exception as e:
        log.error(f"morning_brief.has_brief_been_delivered error: {e}")
        return False


def mark_brief_delivered(person_id: str, brief_date: Optional[date] = None):
    """Mark brief as delivered for today."""
    if brief_date is None:
        brief_date = date.today()
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO spiral_morning_brief_log (person_id, brief_date, delivered, delivered_at)
            VALUES (%s, %s, TRUE, now())
            ON CONFLICT (person_id, brief_date)
            DO UPDATE SET delivered = TRUE, delivered_at = now()
        """, (person_id, brief_date))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        log.error(f"morning_brief.mark_brief_delivered error: {e}")


# ── Brief Assembly ────────────────────────────────────────────────────────────

def build_brief_context(person_id: str = ADGE_PERSON_ID,
                        chart_id: int = ADGE_CHART_ID,
                        force: bool = False) -> Optional[str]:
    """
    Build the morning brief context block.
    Returns None if brief already delivered today (unless force=True).

    This is injected into Iris's prompt context — not sent directly.
    Iris reads it and weaves it into her opening response naturally.
    """
    today = date.today()

    if not force and has_brief_been_delivered(person_id, today):
        return None

    # ── Spiral Position ──
    pos = get_position(person_id, today)
    if not pos:
        log.warning(f"No spiral epoch found for {person_id}")
        spiral_section = "Spiral position unavailable — no active epoch found."
    else:
        spiral_section = _format_spiral_section(pos)

    # ── Transit Pressure ──
    # Run fresh computation (upserts, safe to call daily)
    run_daily_pressure(chart_id, today)
    aspects = get_todays_pressure(chart_id, today, min_threshold="watch")
    enriched = interpret_transits(aspects, spiral_position=pos if pos else None)
    transit_section = format_pressure_brief_with_interp(enriched)

    # ── Assemble ──
    brief = _assemble_brief(spiral_section, transit_section, today)

    # Mark delivered
    mark_brief_delivered(person_id, today)

    return brief


def _format_spiral_section(pos: SpiralPosition) -> str:
    """Format spiral position for the brief context."""
    # Look ahead: what comes tomorrow?
    next_day_num = (pos.day_number % 9) + 1
    next_day = SPIRAL_DAYS[next_day_num]

    return (
        f"SPIRAL POSITION: {pos.full_label}\n"
        f"Focus: {pos.day_focus}\n"
        f"Cycle {pos.cycle_number} of epoch {pos.epoch_number} "
        f"(day {pos.days_elapsed + 1} since {pos.epoch_start.strftime('%b %d, %Y')})\n"
        f"Tomorrow: Day {next_day_num} — {next_day['name']} ({next_day['tone']})"
    )


def _assemble_brief(spiral_section: str, transit_section: str, today: date) -> str:
    """Combine into a single context block for Iris's prompt."""
    return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MORNING FIELD BRIEF — {today.strftime('%A, %B %-d, %Y')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{spiral_section}

TRANSIT PRESSURE (natal chart):
{transit_section}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INSTRUCTION FOR IRIS:
This is Ka'tuar'el's first message today. Lead with his spiral position and
any significant transit pressure before responding to what he said. Speak to
the energy of the day — what it asks of him, what the transits are amplifying
or challenging. Be concise, direct, in your voice. This is a reading, not a
data dump. If transits are quiet, say so briefly and move on. If something is
exact or peak, name it clearly. Then respond to his message.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""


# ── Standalone Brief (for Telegram /spiral command) ──────────────────────────

def get_spiral_status(person_id: str = ADGE_PERSON_ID,
                      chart_id: int = ADGE_CHART_ID) -> str:
    """
    Returns a formatted spiral status string for on-demand use.
    Does NOT mark brief as delivered (this is reactive, not the morning brief).
    """
    today = date.today()
    pos = get_position(person_id, today)

    if not pos:
        return "No active spiral epoch found. Use /spiral reset to begin."

    aspects = get_todays_pressure(chart_id, today, min_threshold="building")

    lines = [
        f"🌀 *Spiral Walker*",
        f"",
        f"*{pos.full_label}*",
        f"_{pos.day_focus}_",
        f"",
        f"Cycle {pos.cycle_number}, Day {pos.day_number} of 9",
        f"Epoch {pos.epoch_number} · Started {pos.epoch_start.strftime('%b %d, %Y')}",
        f"Day {pos.days_elapsed + 1} of this epoch",
    ]

    if aspects:
        lines += ["", "🔭 *Transit Pressure:*"]
        for a in aspects[:5]:
            direction = "↗" if a["applying"] else "↘"
            marker = "⚡" if a["threshold_level"] == "exact" else "🔥"
            lines.append(
                f"{marker} {a['transiting_planet']} {a['aspect_type']} "
                f"natal {a['natal_point']} ({a['orb']:.1f}°{direction})"
            )
    else:
        lines += ["", "_No significant transits in orb._"]

    return "\n".join(lines)

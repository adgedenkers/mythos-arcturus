"""
SEN-0006: Spiral Time Walker — Core Engine

Calculates current spiral position (Cycle.Day) from a person's epoch date.
Manages epoch creation, reset, and history.

The Nine Day Sun Cycle (Ka'tuar'el / Adge Denkers):
  Day 1 — Aris    (Ignition)      — Start. Light the spark.
  Day 2 — Selun   (Descent)       — Listen. Go inward.
  Day 3 — Valen   (Structure)     — Anchor. Build the container.
  Day 4 — Oran    (Motion)        — Act. Get things moving.
  Day 5 — Thael   (Vision)        — Dream. Let meaning emerge.
  Day 6 — Riven   (Severance)     — Release. Cut what's not working.
  Day 7 — Miren   (Return)        — Integrate. Bring it together.
  Day 8 — Kiren   (Service)       — Offer. Share what you've made.
  Day 9 — Sayel   (Sealing)       — Complete. Rest.

Notation: Cycle.Day  (e.g. 18.4 = Cycle 18, Day 4)
Meta-arc:  1 Spiral = 9 Cycles = 81 Days
"""

import logging
import os
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Optional

import psycopg2
import psycopg2.extras

log = logging.getLogger("iris.spiral_engine")

# ── Day Definitions ──────────────────────────────────────────────────────────

SPIRAL_DAYS = {
    1: {"name": "Aris",  "tone": "Ignition",   "focus": "Start. Declare your intention. Light the spark."},
    2: {"name": "Selun", "tone": "Descent",    "focus": "Listen. Drop inward. Breathe. Let things settle."},
    3: {"name": "Valen", "tone": "Structure",  "focus": "Anchor. Define boundaries. Build the container."},
    4: {"name": "Oran",  "tone": "Motion",     "focus": "Act. Take tangible steps. Get things moving."},
    5: {"name": "Thael", "tone": "Vision",     "focus": "Dream. Notice symbols. Let meaning emerge."},
    6: {"name": "Riven", "tone": "Severance",  "focus": "Release. Cut what's not working. Create space."},
    7: {"name": "Miren", "tone": "Return",     "focus": "Integrate. Reflect on what you've learned."},
    8: {"name": "Kiren", "tone": "Service",    "focus": "Offer. Share what you've made. Give back."},
    9: {"name": "Sayel", "tone": "Sealing",    "focus": "Complete. Rest. Seal the cycle with gratitude."},
}

DAYS_PER_CYCLE  = 9
CYCLES_PER_SPIRAL = 9
DAYS_PER_SPIRAL = DAYS_PER_CYCLE * CYCLES_PER_SPIRAL  # 81


# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class SpiralPosition:
    """Current position in the Nine Day Sun Cycle."""
    person_id:    str
    epoch_id:     str          # UUID of the active epoch
    epoch_number: int          # which epoch (resets count up)
    epoch_start:  date         # when this epoch began
    today:        date
    days_elapsed: int          # days since epoch start (0-indexed)

    spiral_number: int         # which 81-day spiral we're in (1-indexed)
    cycle_number:  int         # which 9-day cycle within epoch (1-indexed)
    day_number:    int         # which day within cycle (1-9)

    day_name:  str             # Aris, Selun, Valen...
    day_tone:  str             # Ignition, Descent...
    day_focus: str             # What this day is about

    @property
    def notation(self) -> str:
        """e.g. '18.4'"""
        return f"{self.cycle_number}.{self.day_number}"

    @property
    def full_label(self) -> str:
        """e.g. 'Cycle 18, Day 4 — Oran (Motion)'"""
        return f"Cycle {self.cycle_number}, Day {self.day_number} — {self.day_name} ({self.day_tone})"

    @property
    def day_of_spiral(self) -> int:
        """Day number within the current 81-day spiral (1–81)."""
        return ((self.cycle_number - 1) % CYCLES_PER_SPIRAL) * DAYS_PER_CYCLE + self.day_number

    @property
    def spiral_progress_pct(self) -> float:
        """0.0–1.0 progress through current 81-day spiral."""
        return self.day_of_spiral / DAYS_PER_SPIRAL


# ── DB Connection ─────────────────────────────────────────────────────────────

def _get_conn():
    db_url = os.environ.get("DATABASE_URL", "postgresql://adge@localhost/mythos")
    return psycopg2.connect(db_url)


# ── Core Calculation ──────────────────────────────────────────────────────────

def calculate_position(epoch_start: date, today: Optional[date] = None) -> dict:
    """
    Pure calculation — no DB required.
    Returns dict with cycle_number, day_number, day_name, tone, focus, notation.
    """
    if today is None:
        today = date.today()

    days_elapsed = (today - epoch_start).days  # 0 on epoch start day

    cycle_number = (days_elapsed // DAYS_PER_CYCLE) + 1
    day_number   = (days_elapsed % DAYS_PER_CYCLE) + 1
    spiral_number = ((days_elapsed // DAYS_PER_SPIRAL)) + 1

    day_def = SPIRAL_DAYS[day_number]

    return {
        "days_elapsed":   days_elapsed,
        "spiral_number":  spiral_number,
        "cycle_number":   cycle_number,
        "day_number":     day_number,
        "day_name":       day_def["name"],
        "day_tone":       day_def["tone"],
        "day_focus":      day_def["focus"],
        "notation":       f"{cycle_number}.{day_number}",
        "full_label":     f"Cycle {cycle_number}, Day {day_number} — {day_def['name']} ({day_def['tone']})",
    }


def get_position(person_id: str, today: Optional[date] = None) -> Optional[SpiralPosition]:
    """
    Fetch active epoch for person and compute their current spiral position.
    Returns None if no epoch exists.
    """
    if today is None:
        today = date.today()

    try:
        conn = _get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT epoch_id, epoch_number, started_at
            FROM spiral_epochs
            WHERE person_id = %s AND ended_at IS NULL
            ORDER BY started_at DESC
            LIMIT 1
        """, (person_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        log.error(f"spiral_engine.get_position error: {e}")
        return None

    if not row:
        return None

    epoch_start = row["started_at"]
    if isinstance(epoch_start, datetime):
        epoch_start = epoch_start.date()

    pos = calculate_position(epoch_start, today)

    return SpiralPosition(
        person_id    = person_id,
        epoch_id     = str(row["epoch_id"]),
        epoch_number = row["epoch_number"],
        epoch_start  = epoch_start,
        today        = today,
        days_elapsed  = pos["days_elapsed"],
        spiral_number = pos["spiral_number"],
        cycle_number  = pos["cycle_number"],
        day_number    = pos["day_number"],
        day_name      = pos["day_name"],
        day_tone      = pos["day_tone"],
        day_focus     = pos["day_focus"],
    )


# ── Epoch Management ──────────────────────────────────────────────────────────

def create_epoch(person_id: str, start_date: Optional[date] = None, reason: str = "") -> SpiralPosition:
    """
    Create a new epoch for a person.
    Closes any active epoch first. New epoch = next epoch_number.
    """
    if start_date is None:
        start_date = date.today()

    try:
        conn = _get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Close active epoch
        cur.execute("""
            UPDATE spiral_epochs
            SET ended_at = %s
            WHERE person_id = %s AND ended_at IS NULL
        """, (start_date, person_id))

        # Get next epoch number
        cur.execute("""
            SELECT COALESCE(MAX(epoch_number), 0) + 1 AS next_num
            FROM spiral_epochs WHERE person_id = %s
        """, (person_id,))
        next_num = cur.fetchone()["next_num"]

        # Insert new epoch
        cur.execute("""
            INSERT INTO spiral_epochs (person_id, epoch_number, started_at, reason, metadata)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING epoch_id
        """, (person_id, next_num, start_date, reason or f"Epoch {next_num} reset",
              psycopg2.extras.Json({"system": "nine_day_sun", "notation": "cycle.day"})))

        conn.commit()
        cur.close()
        conn.close()

        log.info(f"Created epoch {next_num} for {person_id} starting {start_date}")
        return get_position(person_id)

    except Exception as e:
        log.error(f"spiral_engine.create_epoch error: {e}")
        raise


def reset_spiral(person_id: str, reason: str = "") -> SpiralPosition:
    """
    Reset a person's spiral to today = Cycle 1, Day 1 of new epoch.
    This is the public-facing 'start fresh' operation.
    """
    return create_epoch(person_id, date.today(), reason or "Manual spiral reset")


def get_epoch_history(person_id: str) -> list:
    """Return all epochs for a person, newest first."""
    try:
        conn = _get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT epoch_id, epoch_number, started_at, ended_at, reason
            FROM spiral_epochs
            WHERE person_id = %s
            ORDER BY epoch_number DESC
        """, (person_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        log.error(f"spiral_engine.get_epoch_history error: {e}")
        return []


# ── Convenience ───────────────────────────────────────────────────────────────

def get_adge_position(today: Optional[date] = None) -> Optional[SpiralPosition]:
    """Shortcut for Ka'tuar'el's spiral position."""
    return get_position("adge", today)


def format_position_brief(pos: SpiralPosition) -> str:
    """Short one-line summary for inclusion in prompts."""
    return (
        f"Spiral position: {pos.full_label}. "
        f"{pos.day_focus}"
    )

#!/usr/bin/env python3
"""
SEN-0011: transit_pressure.py DB connection + natal positions hotfix

Root cause (found via diag after SEN-0010):
  _get_conn() uses DATABASE_URL env var which defaults to
  "postgresql://adge@localhost/mythos" — a TCP connection that requires
  a password. Mythos convention is Unix socket: host='/var/run/postgresql'.
  This caused _load_natal_positions() to fail silently, returning {},
  which left the transit engine with no natal data → no aspects → empty
  /transits output.

  Additionally, SEN-0009 injected _load_natal_positions_via_generator()
  but never wired it as the implementation of _load_natal_positions().
  The original (broken) function was still being called.

What this patch changes:
1. Fix _get_conn() — replace DATABASE_URL default with explicit socket
   connection matching the rest of Mythos (same as natal_generator.py).

2. Wire _load_natal_positions_via_generator() — replace the body of
   _load_natal_positions() to call our generator function (which uses
   the correct socket connection) and fall back to the fixed _get_conn()
   if needed.

Tables touched: reads spiral_transit_pressure, astro_natal_charts,
                astro_chart_objects, astro_chart_points
Services restarted: none (transit_pressure is imported on demand,
                    not a running service)
Blast radius: LOW — two in-place edits, same file
Gating: _load_natal_positions returns >= 9 natal points for chart_id=9 +
        all 5 golden fixtures pass
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

TRANSIT_PRESSURE_PATH = Path('/opt/mythos/astrology/spiral/transit_pressure.py')
CHECK_ACCURACY_PATH   = '/opt/mythos/astrology/tests/check_accuracy.py'

# ─── Fix 1: _get_conn() ───────────────────────────────────────────────────
# Old: reads DATABASE_URL, defaults to TCP localhost (requires password)
# New: direct socket connection matching natal_generator.py

GET_CONN_OLD = (
    '    db_url = os.environ.get("DATABASE_URL", "postgresql://adge@localhost/mythos")\n'
    '    return psycopg2.connect(db_url)'
)

GET_CONN_NEW = (
    '    # SEN-0011: use Unix socket (no password required), matching natal_generator.py\n'
    '    # DATABASE_URL TCP default was failing with "no password supplied"\n'
    '    return psycopg2.connect(\n'
    '        host="/var/run/postgresql",\n'
    '        port=5432,\n'
    '        database="mythos",\n'
    '        user="adge",\n'
    '    )'
)

# ─── Fix 2: wire _load_natal_positions_via_generator ─────────────────────
# Replace _load_natal_positions body so it calls our generator function.
# The generator function was injected by SEN-0009 but never called.

NATAL_POS_OLD = '''def _load_natal_positions(chart_id: int) -> dict:
    """
    Load natal ecliptic longitudes from astro_chart_points table.
    Returns dict: point_name -> longitude
    """
    try:
        conn = _get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Chart points (planets)
        cur.execute("""
            SELECT name, longitude
            FROM astro_chart_points
            WHERE chart_id = %s
        """, (chart_id,))
        points = {row["name"]: row["longitude"] for row in cur.fetchall()}

        # House cusps for ASC (house 1) and MC (house 10)
        cur.execute("""
            SELECT house_number, longitude
            FROM astro_natal_house_cusps
            WHERE chart_id = %s AND house_number IN (1, 10)
        """, (chart_id,))
        for row in cur.fetchall():
            if row["house_number"] == 1:
                points["ASC"] = row["longitude"]
            elif row["house_number"] == 10:
                points["MC"] = row["longitude"]

        cur.close()
        conn.close()

        # Filter to only the natal points we care about
        return {k: v for k, v in points.items() if k in NATAL_POINTS}

    except Exception as e:
        log.error(f"transit_pressure._load_natal_positions error: {e}")
        return {}'''

NATAL_POS_NEW = '''def _load_natal_positions(chart_id: int) -> dict:
    """
    Load natal ecliptic longitudes for transit pressure computation.
    Returns dict: point_name -> longitude, filtered to NATAL_POINTS.

    SEN-0011: now calls _load_natal_positions_via_generator() first
    (injected by SEN-0009, uses natal_generator.load_natal() via socket).
    Falls back to direct Postgres query via fixed _get_conn() if needed.
    """
    # Try natal_generator path first (SEN-0009 injection)
    try:
        positions = _load_natal_positions_via_generator(chart_id)
        if positions:
            # Normalise point names: astro_chart_points stores 'Ascendant'/'Midheaven'
            # but NATAL_POINTS uses 'ASC'/'MC'
            NAME_MAP = {
                'Ascendant': 'ASC',
                'Midheaven': 'MC',
                'Mean Node': 'North Node',
                'True Node': 'North Node',
            }
            normalised = {}
            for k, v in positions.items():
                normalised[NAME_MAP.get(k, k)] = v
            # Filter to NATAL_POINTS (generator returns all chart_objects)
            filtered = {k: v for k, v in normalised.items() if k in NATAL_POINTS}
            if filtered:
                log.debug(
                    "_load_natal_positions: %d points via natal_generator for chart_id=%d",
                    len(filtered), chart_id
                )
                return filtered
    except Exception as e:
        log.warning("natal_generator path failed: %s", e)

    # Fallback: direct Postgres query via socket connection
    log.warning(
        "_load_natal_positions: falling back to direct Postgres for chart_id=%d",
        chart_id
    )
    try:
        conn = _get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Chart objects (planets) from astro_chart_objects
        cur.execute(
            "SELECT object_name, longitude FROM astro_chart_objects WHERE chart_id = %s",
            (chart_id,)
        )
        points = {row["object_name"]: row["longitude"] for row in cur.fetchall()}

        # ASC and MC from astro_chart_points (stored as 'Ascendant'/'Midheaven')
        NAME_MAP = {'Ascendant': 'ASC', 'Midheaven': 'MC',
                    'Mean Node': 'North Node', 'True Node': 'North Node'}
        cur.execute(
            "SELECT point_name, longitude FROM astro_chart_points WHERE chart_id = %s",
            (chart_id,)
        )
        for row in cur.fetchall():
            mapped = NAME_MAP.get(row["point_name"], row["point_name"])
            points[mapped] = row["longitude"]

        # House 1 = ASC, house 10 = MC from cusps if not already set
        if "ASC" not in points or "MC" not in points:
            cur.execute(
                "SELECT house_number, cusp_longitude FROM astro_natal_house_cusps "
                "WHERE chart_id = %s AND house_number IN (1, 10)",
                (chart_id,)
            )
            for row in cur.fetchall():
                if row["house_number"] == 1:
                    points.setdefault("ASC", row["cusp_longitude"])
                elif row["house_number"] == 10:
                    points.setdefault("MC", row["cusp_longitude"])

        cur.close()
        conn.close()

        filtered = {k: v for k, v in points.items() if k in NATAL_POINTS}
        if filtered:
            log.info(
                "_load_natal_positions: %d points via direct Postgres for chart_id=%d",
                len(filtered), chart_id
            )
        else:
            log.error(
                "_load_natal_positions: no natal points found for chart_id=%d",
                chart_id
            )
        return filtered

    except Exception as e:
        log.error("_load_natal_positions error (fallback also failed): %s", e)
        return {}'''


def log(patch, msg):
    patch.logger.log(msg)


def edit_file(patch, path, old_str, new_str, label, backup_suffix='.sen0011.bak'):
    current = path.read_text()
    if new_str in current:
        patch.validations.append(f"{label}: already applied")
        log(patch, f"  ✓ {label}: already applied (idempotent)")
        return True
    count = current.count(old_str)
    if count == 0:
        patch.errors.append(f"{label}: anchor not found")
        log(patch, f"  ✗ {label}: anchor not found")
        return False
    if count > 1:
        patch.errors.append(f"{label}: anchor ambiguous ({count}x)")
        log(patch, f"  ✗ {label}: anchor ambiguous ({count}x)")
        return False
    backup = path.with_suffix(path.suffix + backup_suffix)
    backup.write_text(current)
    updated = current.replace(old_str, new_str, 1)
    path.write_text(updated)
    verify = path.read_text()
    if new_str not in verify or old_str in verify:
        path.write_text(current)
        patch.errors.append(f"{label}: post-edit verify failed")
        log(patch, f"  ✗ {label}: post-edit verify failed, restored")
        return False
    import py_compile
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as e:
        path.write_text(current)
        patch.errors.append(f"{label}: py_compile failed: {e}")
        log(patch, f"  ✗ {label}: py_compile FAILED, restored")
        return False
    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(path))
    log(patch, f"  ✓ {label}: applied and verified")
    return True


def verify_natal_positions(patch) -> bool:
    """Confirm _load_natal_positions now returns >= 9 points for Adge."""
    cmd = [
        '/opt/mythos/.venv/bin/python3', '-c',
        'import sys; sys.path.insert(0, "/opt/mythos"); '
        'from astrology.spiral.transit_pressure import _load_natal_positions; '
        'pos = _load_natal_positions(9); '
        'print("positions:", len(pos), list(pos.keys())[:5]); '
        'assert len(pos) >= 9, f"only {len(pos)} positions"',
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        patch.errors.append(f"natal positions still failing: {out.stderr.strip()[:300]}")
        log(patch, f"  ✗ still failing: {out.stderr.strip()[:200]}")
        return False
    log(patch, f"  ✓ {out.stdout.strip()}")
    return True


def verify_transits_return_data(patch) -> bool:
    """Confirm compute_daily_pressure returns aspects for 2026-04-28."""
    cmd = [
        '/opt/mythos/.venv/bin/python3', '-c',
        'import sys; sys.path.insert(0, "/opt/mythos"); '
        'from datetime import date; '
        'from astrology.spiral.transit_pressure import compute_daily_pressure; '
        'aspects = compute_daily_pressure(chart_id=9, target_date=date(2026, 4, 28)); '
        'print("aspects on 2026-04-28:", len(aspects)); '
        'assert len(aspects) > 0, "still empty"; '
        '[print(f"  {a[\'transiting_planet\']} {a[\'aspect_type\']} natal {a[\'natal_point\']} orb={a[\'orb\']:.3f}°") for a in aspects[:4]]',
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        patch.errors.append(f"transit computation still empty: {out.stderr.strip()[:300]}")
        log(patch, f"  ✗ still empty: {out.stderr.strip()[:200]}")
        return False
    for line in out.stdout.strip().splitlines():
        log(patch, f"  {line}")
    return True


def run_golden_fixtures(patch) -> bool:
    result = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', CHECK_ACCURACY_PATH],
        capture_output=True, text=True, timeout=60,
    )
    log(patch, "  — golden fixture output —")
    for line in result.stdout.splitlines():
        log(patch, f"    {line}")
    if result.returncode == 0:
        log(patch, "  ✓ all 5 golden fixtures PASS")
        return True
    patch.errors.append(f"golden fixtures failed (exit {result.returncode})")
    return False


# ═══════════════════════════════════════════════════════════════════════
patch = PatchBase(
    stream='SEN',
    number=11,
    description='transit_pressure db connection + natal positions fix',
    patch_type='PATCH',
)
patch.begin()

print('\n' + '=' * 70)
print('SEN-0011 — transit_pressure.py DB connection hotfix')
print('Root cause: _get_conn() using TCP localhost (password) not socket')
print('=' * 70 + '\n')

if not TRANSIT_PRESSURE_PATH.exists():
    print('✗ transit_pressure.py missing')
    patch.errors.append('transit_pressure.py missing')
    patch.finish()
    sys.exit(1)

# ─── PHASE 1: Fix _get_conn() ────────────────────────────────────
print('PHASE 1: Fix _get_conn() — socket connection')
print('-' * 70)
if not edit_file(patch, TRANSIT_PRESSURE_PATH, GET_CONN_OLD, GET_CONN_NEW, '_get_conn'):
    patch.finish(); sys.exit(1)

# ─── PHASE 2: Wire _load_natal_positions ─────────────────────────
print('\nPHASE 2: Wire _load_natal_positions to call natal_generator')
print('-' * 70)
if not edit_file(patch, TRANSIT_PRESSURE_PATH, NATAL_POS_OLD, NATAL_POS_NEW, '_load_natal_positions'):
    patch.finish(); sys.exit(1)

# ─── PHASE 3: Verify natal positions now load ────────────────────
print('\nPHASE 3: Verify _load_natal_positions returns data')
print('-' * 70)
if not verify_natal_positions(patch):
    patch.finish(); sys.exit(1)

# ─── PHASE 4: Verify transits compute on 2026-04-28 ─────────────
print('\nPHASE 4: Verify compute_daily_pressure returns aspects')
print('-' * 70)
if not verify_transits_return_data(patch):
    patch.finish(); sys.exit(1)

# ─── PHASE 5: Golden fixtures ────────────────────────────────────
print('\nPHASE 5: Golden fixture regression check')
print('-' * 70)
if not run_golden_fixtures(patch):
    patch.finish(); sys.exit(1)

print('\n' + '=' * 70)
print('✓ SEN-0011 complete — /transits now returns data')
print('=' * 70 + '\n')

patch.finish()

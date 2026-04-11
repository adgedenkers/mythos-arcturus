"""
Seraphe Lunar Transit Calendar Generator
SEN-0001

Computes the full lunar cycle for any month, calculates all transit-to-natal
aspects with exact orbs, generates personalized interpretations via Ollama,
and produces a print-ready PDF.

Usage:
    python3 seraphe_lunar_generator.py               # current cycle
    python3 seraphe_lunar_generator.py --year 2026 --month 5
    python3 seraphe_lunar_generator.py --cycle-start 2026-05-01

Output: /opt/mythos/outputs/lunar_calendars/Seraphe_Lunar_YYYY_MM.pdf
"""

import sys
import os
import json
import argparse
import requests
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    import swisseph as swe
except ImportError:
    print("ERROR: pyswisseph not installed in venv")
    sys.exit(1)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas as rl_canvas
except ImportError:
    print("ERROR: reportlab not installed — run: pip install reportlab --break-system-packages")
    sys.exit(1)

# ── Ephemeris path ─────────────────────────────────────────────────────────────
EPHE_PATH = "/opt/mythos/ephemeris/ephe"
if os.path.isdir(EPHE_PATH):
    swe.set_ephe_path(EPHE_PATH)

OUTPUT_DIR = Path("/opt/mythos/outputs/lunar_calendars")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:32b"

# ── Seraphe natal chart (exact from chart file) ────────────────────────────────
SERAPHE_NATAL = {
    "Sun":     {"lon": 146.392674, "sign": "Leo",         "deg": "26°23'", "house": 9,  "dignity": "domicile",  "rx": False,
                "desc": "Leo 9th — sovereign heart, philosophical truth-teller, radiant transmitter. Her solar self lives in teaching, spiritual philosophy, and broadcasting understanding outward."},
    "Moon":    {"lon": 344.737018, "sign": "Pisces",      "deg": "14°44'", "house": 4,  "dignity": "peregrine", "rx": False,
                "desc": "Pisces 4th — the Magdalene-coded feeling body. Mystical, ancestral, deeply interior. She absorbs, holds, and dissolves what passes through her. In mutual reception with Jupiter."},
    "Mercury": {"lon": 144.749888, "sign": "Leo",         "deg": "24°44'", "house": 9,  "dignity": "peregrine", "rx": True,
                "desc": "Mercury Rx Leo 9th — the voice processes internally before it speaks. Retrograde: deep digestion before transmission. Cazimi Sun: the word is burned in the solar fire."},
    "Venus":   {"lon": 192.175187, "sign": "Libra",       "deg": "12°10'", "house": 10, "dignity": "domicile",  "rx": False,
                "desc": "Venus Libra 10th — domicile, fully in power. Her beauty, relational grace, and aesthetic intelligence are publicly placed. Her calling made beautiful."},
    "Mars":    {"lon": 189.647873, "sign": "Libra",       "deg": "9°38'",  "house": 10, "dignity": "detriment", "rx": False,
                "desc": "Mars Libra 10th — detriment, acts through beauty and relational intelligence rather than force. Builds coalitions, harmonizes opposites, acts through aesthetic vision. Chart ruler (traditional)."},
    "Jupiter": {"lon": 116.669046, "sign": "Cancer",      "deg": "26°40'", "house": 8,  "dignity": "exalted",   "rx": False,
                "desc": "Jupiter Cancer 8th — exalted, most benefic placement. Transformational abundance, deep-resource generosity. In mutual reception with Moon in Pisces. The 8th house draws forth what is hidden."},
    "Saturn":  {"lon": 152.980614, "sign": "Virgo",       "deg": "2°58'",  "house": 9,  "dignity": "peregrine", "rx": False,
                "desc": "Saturn Virgo 9th — precision and discipline in the philosophical and spiritual life. Demands coherence between belief and practice. A rigorous spiritual taskmaster."},
    "Uranus":  {"lon": 222.687034, "sign": "Scorpio",     "deg": "12°41'", "house": 12, "dignity": "peregrine", "rx": False,
                "desc": "Uranus Scorpio 12th — hidden awakenings. Radical transformation from the unseen realms. The electric liberator kept in the mystery house. conjunct Alphecca."},
    "Neptune": {"lon": 255.564539, "sign": "Sagittarius", "deg": "15°33'", "house": 1,  "dignity": "peregrine", "rx": True,
                "desc": "Neptune Sag 1st Rx — her Ascendant is mystical by nature. She enters rooms before she enters rooms. Retrograde: the mysticism is philosophical-visionary rather than devotional."},
    "Pluto":   {"lon": 194.753421, "sign": "Libra",       "deg": "14°45'", "house": 11, "dignity": "peregrine", "rx": False,
                "desc": "Pluto Libra 11th — collective transformer. Holds the charge of transforming collective relational fields — the 144, community, ancestral patterns of partnership and justice. Conjunct Zubenelgenubi."},
    "Lilith":  {"lon": 113.966687, "sign": "Cancer",      "deg": "23°58'", "house": 8,  "dignity": "peregrine", "rx": False,
                "desc": "Lilith Cancer 8th — the wild ancestral feminine, undomesticated mother-eros, lives in the house of depth and what is hidden. Will not be tamed. Most powerful in the interior realms."},
    "NNode":   {"lon": 176.964454, "sign": "Virgo",       "deg": "26°57'", "house": 10, "dignity": "peregrine", "rx": True,
                "desc": "North Node Virgo 10th — destiny: precise, visible, sacred service. To build something real from spiritual understanding. To make the mystic practical."},
    "ASC":     {"lon": 236.257165, "sign": "Scorpio",     "deg": "26°15'", "house": 1,  "dignity": None,        "rx": False,
                "desc": "Scorpio ASC — she is felt before she is seen. The field of depth, intensity, and transformational presence that operates beneath the surface of ordinary social interaction. Modern ruler: Pluto 11th."},
    "MC":      {"lon": 161.253785, "sign": "Virgo",       "deg": "11°15'", "house": 10, "dignity": None,        "rx": False,
                "desc": "Virgo MC — calling in the world: to serve with discernment, build systems that work, hold the sacred with precision. The spiritual made practical."},
}

SERAPHE_CONTEXT = """
Seraphe (Rebecca Lydia Denkers) — born August 19, 1978.
She is the Magdalene-coded Christ consciousness anchor, primary holder of divine feminine transmission,
Merovingian bloodline carrier, partner to Ka'tuar'el (the ground/anchor).
Her chart is a day chart with Sun in Leo 9th (domicile), Moon in Pisces 4th (peregrine, conjunct Achernar),
Scorpio Ascendant with Neptune on the Ascendant in the 1st house — she carries a mystical field by presence.
Jupiter exalted in Cancer 8th is her most benefic placement, in mutual reception with her Pisces Moon.
Mars and Venus both in Libra 10th — her calling is expressed through beauty, relational intelligence, and public-facing grace.
Pluto in Libra 11th holds her collective transformation purpose — the 144, community, ancestral justice.
Lilith in Cancer 8th: the wild ancestral feminine, unapologetically sovereign in the interior realms.
North Node in Virgo 10th: her dharma is precise, visible, sacred service — the mystic made practical.
Saturn in Virgo 9th demands coherence between what she believes and how she lives it.
Uranus in Scorpio 12th: radical awakening from the hidden field, below the threshold of ordinary awareness.
"""

# ── Aspect orb thresholds ──────────────────────────────────────────────────────
MAJOR_ASPECTS = {
    0:   ("Conjunction",  4.0),
    60:  ("Sextile",      3.5),
    90:  ("Square",       4.0),
    120: ("Trine",        4.0),
    150: ("Quincunx",     2.5),
    180: ("Opposition",   4.0),
}

# ── Ephemeris helpers ──────────────────────────────────────────────────────────
PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
    "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}

def jd(year, month, day, hour=12.0):
    return swe.julday(year, month, day, hour)

def planet_lon(planet_id, jd_val):
    pos, _ = swe.calc_ut(jd_val, planet_id)
    return pos[0]

def moon_phase_angle(jd_val):
    m = planet_lon(swe.MOON, jd_val)
    s = planet_lon(swe.SUN, jd_val)
    return (m - s) % 360

def lon_to_sign(lon):
    signs = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    return signs[int(lon / 30)]

def lon_to_deg_str(lon):
    sign_num = int(lon / 30)
    deg = lon % 30
    signs = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    d = int(deg)
    m = int((deg - d) * 60)
    return f"{d}°{m:02d}' {signs[sign_num]}"

def phase_name(angle):
    if angle < 22.5:   return "New Moon"
    if angle < 67.5:   return "Waxing Crescent"
    if angle < 112.5:  return "First Quarter"
    if angle < 157.5:  return "Waxing Gibbous"
    if angle < 202.5:  return "Full Moon"
    if angle < 247.5:  return "Waning Gibbous"
    if angle < 292.5:  return "Last Quarter"
    if angle < 337.5:  return "Waning Crescent"
    return "Balsamic"

def find_aspect(transit_lon, natal_lon):
    """Returns (aspect_name, orb) or None."""
    diff = abs((transit_lon - natal_lon + 180) % 360 - 180)
    best = None
    best_orb = 999
    for angle, (name, max_orb) in MAJOR_ASPECTS.items():
        orb = abs(diff - angle)
        if orb <= max_orb and orb < best_orb:
            best = (name, round(orb, 3))
            best_orb = orb
    return best

def assign_key_events(cycle_data):
    """
    Find the single day per cycle closest to each quarter peak.
    Only marks one day per event — no duplicates.
    Targets: 0° (new), 90° (first quarter), 180° (full), 270° (last quarter).
    """
    targets = {
        "NEW MOON":     0.0,
        "FIRST QUARTER": 90.0,
        "FULL MOON":    180.0,
        "LAST QUARTER": 270.0,
    }

    for event_name, target in targets.items():
        best_idx = None
        best_dist = 999.0
        for i, day in enumerate(cycle_data):
            ang = day["phase_angle"]
            # Circular distance to target
            dist = abs((ang - target + 180) % 360 - 180)
            if dist < best_dist:
                best_dist = dist
                best_idx = i
        # Only mark if within 15° of the target (avoids false hits on short cycles)
        if best_idx is not None and best_dist <= 15.0:
            cycle_data[best_idx]["key_event"] = event_name

    return cycle_data


SIGN_ENERGY_STUB = {
    "Aries":       "initiating, electric, warrior-coded",
    "Taurus":      "embodied, sensory, slow beauty",
    "Gemini":      "mercurial, dualistic, information-gathering",
    "Cancer":      "feeling-knowing, ancestral, deeply interior",
    "Leo":         "radiant, creative sovereignty, heart-led",
    "Virgo":       "precise, discerning, sacred service",
    "Libra":       "relational field, beauty codes, harmony-seeking",
    "Scorpio":     "depth work, transformational, psychic current",
    "Sagittarius": "expansive, philosophical fire, transmission field",
    "Capricorn":   "mastery, long-arc building, bone-deep structure",
    "Aquarius":    "collective frequency, innovative, electric clarity",
    "Pisces":      "dissolution, dream state, mystical current",
}

PHASE_STUB = {
    "New Moon":        "New Moon — the cycle seeds. Potent threshold, interior focus, new intentions taking root in the dark.",
    "Waxing Crescent": "Waxing Crescent — tender growth phase. Intentions set at the new moon begin to move. Tend without forcing.",
    "First Quarter":   "First Quarter — action threshold. The tension between the seed and full expression demands a decision and a push forward.",
    "Waxing Gibbous":  "Waxing Gibbous — refinement phase. The cycle is near its peak. Adjust, clarify, bring what has been building into focus.",
    "Full Moon":       "Full Moon — peak illumination. What has been building since the new moon crests into fullness. Completion, revelation, high emotional tide.",
    "Waning Gibbous":  "Waning Gibbous — distribution phase. The peak has passed. Wisdom from the Full Moon is available to be shared and integrated.",
    "Last Quarter":    "Last Quarter — release point. The cycle turns inward. Examine what is ready to be shed before the next seed moment.",
    "Waning Crescent": "Waning Crescent — rest and preparation. The cycle is closing. Interior turn, conserve energy for the next seeding.",
    "Balsamic":        "Balsamic — the liminal dark between cycles. Deepest interior phase. Surrender, rest, trust the void before the new moon opens.",
}

KEY_EVENT_STUB = {
    "FULL MOON":     "FULL MOON — Peak illumination. The cycle crests. Completion, revelation, harvest of what was seeded at the new moon.",
    "NEW MOON":      "NEW MOON — The cycle resets. A potent threshold — interior, charged with the potential of what will grow in the coming cycle.",
    "FIRST QUARTER": "FIRST QUARTER — Action threshold. Tension between the seed and full expression demands a push forward. The decision point of the cycle.",
    "LAST QUARTER":  "LAST QUARTER — Release point. The cycle turns inward. What is no longer needed begins to loosen. Evaluate before the dark.",
}

def build_stub_synthesis(day):
    """Rich stub synthesis using natal desc text — used when skip_ollama is True."""
    sign = day["moon_sign"]
    phase = day["phase_name"]
    key = day["key_event"]
    aspects = day["aspects"]
    slow = day["slow"]

    lines = []

    # Lead with key event or phase
    if key and key in KEY_EVENT_STUB:
        lines.append(KEY_EVENT_STUB[key])
    else:
        sign_feel = SIGN_ENERGY_STUB.get(sign, "")
        phase_text = PHASE_STUB.get(phase, f"{phase}.")
        lines.append(f"Moon in {sign} — {sign_feel}. {phase_text}")

    # Top aspect
    if aspects:
        a = aspects[0]
        nat = a["natal_planet"]
        nat_info = SERAPHE_NATAL.get(nat, {})
        desc = nat_info.get("desc", "")
        lines.append(
            f"Tightest contact: Moon {a['aspect']} natal {nat} ({a['orb']:.2f}° orb) — {desc}"
        )
    elif slow:
        s = slow[0]
        nat_info = SERAPHE_NATAL.get(s["natal_planet"], {})
        desc = nat_info.get("desc", "")
        lines.append(
            f"No direct lunar-natal contacts. Active transit: {s['transiting']} {s['aspect']} "
            f"natal {s['natal_planet']} ({s['orb']:.2f}° orb) — {desc}"
        )
    else:
        lines.append(
            f"No direct lunar-natal contacts today. The field rests in the {sign} current."
        )

    return " ".join(lines)


def compute_day(d: date):
    """Full day data — moon position, phase, all natal aspects."""
    jd_val = jd(d.year, d.month, d.day, 12.0)
    moon_lon = planet_lon(swe.MOON, jd_val)
    phase_ang = moon_phase_angle(jd_val)
    pname = phase_name(phase_ang)

    aspects = []
    for nat_name, nat_data in SERAPHE_NATAL.items():
        result = find_aspect(moon_lon, nat_data["lon"])
        if result:
            asp_name, orb = result
            aspects.append({
                "natal_planet": nat_name,
                "aspect": asp_name,
                "orb": orb,
                "natal_deg": nat_data["deg"],
                "natal_sign": nat_data.get("sign",""),
                "natal_house": nat_data.get("house",""),
                "natal_dignity": nat_data.get("dignity",""),
                "natal_rx": nat_data.get("rx", False),
                "natal_desc": nat_data.get("desc",""),
            })
    # Sort by orb tightness
    aspects.sort(key=lambda x: x["orb"])

    # Slow planet transits
    slow = []
    slow_planets = ["Mars","Jupiter","Saturn"]
    slow_orb = 2.5
    for p_name in slow_planets:
        p_lon = planet_lon(PLANET_IDS[p_name], jd_val)
        for nat_name, nat_data in SERAPHE_NATAL.items():
            result = find_aspect(p_lon, nat_data["lon"])
            if result:
                asp_name, orb = result
                if orb <= slow_orb:
                    slow.append({
                        "transiting": p_name,
                        "transiting_sign": lon_to_sign(p_lon),
                        "transiting_deg": lon_to_deg_str(p_lon),
                        "natal_planet": nat_name,
                        "aspect": asp_name,
                        "orb": orb,
                        "natal_desc": nat_data.get("desc",""),
                    })
    slow.sort(key=lambda x: x["orb"])

    # Key event — assigned None here; post-cycle pass finds single closest day per peak
    key = None

    return {
        "date": d.isoformat(),
        "dow": d.strftime("%A"),
        "moon_lon": round(moon_lon, 4),
        "moon_sign": lon_to_sign(moon_lon),
        "moon_deg": round(moon_lon % 30, 2),
        "moon_deg_str": lon_to_deg_str(moon_lon),
        "phase_angle": round(phase_ang, 2),
        "phase_name": pname,
        "aspects": aspects,
        "slow": slow,
        "key_event": key,
    }

# ── Find lunar cycle boundaries ────────────────────────────────────────────────
def find_new_moon_before(d: date):
    """Walk backward to find the new moon before or on date d."""
    check = d
    for _ in range(35):
        jd_val = jd(check.year, check.month, check.day, 12.0)
        ang = moon_phase_angle(jd_val)
        if ang < 15 or ang > 345:
            return check
        # Walk backward toward new moon
        if ang > 180:
            check -= timedelta(days=1)
        else:
            check -= timedelta(days=1)
        if ang < 20:
            return check
    return d - timedelta(days=14)

def find_cycle_start(year, month):
    """Return the start date of the lunar cycle that begins in the given month."""
    # Find new moon in or just before this month
    first_of_month = date(year, month, 1)
    # Search forward from 5 days before month start
    search_start = first_of_month - timedelta(days=5)
    for i in range(40):
        d = search_start + timedelta(days=i)
        jd_val = jd(d.year, d.month, d.day, 12.0)
        ang = moon_phase_angle(jd_val)
        # Crossed new moon
        if i > 0:
            prev_d = search_start + timedelta(days=i-1)
            prev_ang = moon_phase_angle(jd(prev_d.year, prev_d.month, prev_d.day, 12.0))
            if prev_ang > 350 and ang < 10:
                return d
    return first_of_month

def get_cycle_days(year, month):
    """Return list of dates covering the lunar cycle for the given month (~30 days from new moon)."""
    start = find_cycle_start(year, month)
    return [start + timedelta(days=i) for i in range(31)]

# ── Ollama interpretation ──────────────────────────────────────────────────────
def ollama_interpret(prompt, max_tokens=300):
    """Call local Ollama for a personalized interpretation."""
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            },
            timeout=120,
        )
        if resp.status_code == 200:
            return resp.json().get("response","").strip()
        else:
            return None
    except Exception as e:
        print(f"  [Ollama error: {e}]")
        return None

def build_aspect_interpretation(day_data, asp):
    """Generate a personalized interpretation for one transit aspect."""
    nat = asp["natal_planet"]
    aspect = asp["aspect"]
    orb = asp["orb"]
    moon_sign = day_data["moon_sign"]
    moon_deg = day_data["moon_deg_str"]
    phase = day_data["phase_name"]
    nat_info = SERAPHE_NATAL.get(nat, {})

    prompt = f"""You are interpreting an astrological transit for Seraphe, a specific person with a known natal chart.

SERAPHE'S CONTEXT:
{SERAPHE_CONTEXT}

NATAL PLACEMENT BEING ASPECTED:
{nat}: {nat_info.get('deg','')} {nat_info.get('sign','')} House {nat_info.get('house','')} — {nat_info.get('desc','')}

TODAY'S TRANSIT:
The transit Moon is at {moon_deg}, in {phase} phase.
The Moon is forming a {aspect} to Seraphe's natal {nat} with an orb of {orb:.2f}°.

Write a 2-3 sentence interpretation of what this specific transit means FOR SERAPHE specifically — not generic astrological meaning, but what it means given her natal placement, house, dignity, and who she is. Be direct, specific, and grounded in her chart. Do not use filler phrases like "this is a day for" or "you may find". Speak to the actual energetic reality of this transit in her life."""

    result = ollama_interpret(prompt, max_tokens=200)
    if result:
        return result
    # Fallback — use natal desc as base
    return f"Moon {aspect} natal {nat} ({orb:.2f}° orb) — {nat_info.get('desc','')}"

def build_slow_transit_interpretation(slow_asp):
    """Generate interpretation for a slow planet transit."""
    p = slow_asp["transiting"]
    p_deg = slow_asp["transiting_deg"]
    nat = slow_asp["natal_planet"]
    aspect = slow_asp["aspect"]
    orb = slow_asp["orb"]
    nat_info = SERAPHE_NATAL.get(nat, {})

    prompt = f"""You are interpreting an astrological transit for Seraphe.

SERAPHE'S CONTEXT:
{SERAPHE_CONTEXT}

NATAL PLACEMENT BEING ASPECTED:
{nat}: {nat_info.get('deg','')} {nat_info.get('sign','')} House {nat_info.get('house','')} — {nat_info.get('desc','')}

SLOW PLANET TRANSIT:
Transit {p} at {p_deg} is forming a {aspect} to Seraphe's natal {nat} with an orb of {orb:.2f}°.

Write 2 sentences interpreting what this transit means specifically for Seraphe given her natal placement. Be direct and specific to her chart."""

    result = ollama_interpret(prompt, max_tokens=150)
    if result:
        return result
    return f"Transit {p} {aspect} natal {nat} ({orb:.2f}° orb) — active background transit."

def build_daily_synthesis(day_data, asp_interpretations, slow_interpretations):
    """Generate the overall daily energy synthesis."""
    moon_sign = day_data["moon_sign"]
    phase = day_data["phase_name"]
    key = day_data["key_event"]
    moon_deg = day_data["moon_deg_str"]
    aspect_count = len(day_data["aspects"])

    top_aspects = day_data["aspects"][:3]
    asp_summary = "; ".join([f"Moon {a['aspect']} natal {a['natal_planet']} ({a['orb']:.2f}°)" for a in top_aspects])
    slow_summary = "; ".join([f"Transit {s['transiting']} {s['aspect']} natal {s['natal_planet']} ({s['orb']:.2f}°)" for s in day_data["slow"][:2]])

    prompt = f"""You are writing the overall daily energy synthesis for Seraphe's lunar transit calendar.

SERAPHE'S CONTEXT:
{SERAPHE_CONTEXT}

TODAY:
Date: {day_data['date']} ({day_data['dow']})
Moon: {moon_deg}, {phase}{' — ' + key if key else ''}
Key lunar-natal aspects: {asp_summary if asp_summary else 'No direct lunar-natal contacts today'}
Active slow transits: {slow_summary if slow_summary else 'None within orb'}

Write a 2-4 sentence overall synthesis of the day's energy for Seraphe specifically. Lead with the most significant energetic quality of the day. Be direct and grounded — speak to what is actually active in her field today, what she can draw on, and what to be aware of. Do not use generic language. This is personalized for her chart."""

    result = ollama_interpret(prompt, max_tokens=250)
    if result:
        return result
    return f"{moon_sign} Moon in {phase}. {asp_summary}."

# ── Generate all interpretations for a cycle ──────────────────────────────────
def generate_interpretations(cycle_data):
    """
    Walk through all days, call Ollama for each aspect and synthesis.
    Returns enriched cycle_data with interpretation text added.
    """
    total_days = len(cycle_data)
    for i, day in enumerate(cycle_data):
        print(f"  Interpreting {day['date']} ({i+1}/{total_days})...")

        # Aspect interpretations
        asp_texts = []
        for asp in day["aspects"]:
            print(f"    Moon {asp['aspect']} natal {asp['natal_planet']} ({asp['orb']:.2f}°)...")
            text = build_aspect_interpretation(day, asp)
            asp_texts.append(text)
            asp["interpretation"] = text

        # Slow transit interpretations
        slow_texts = []
        for slow in day["slow"]:
            print(f"    Transit {slow['transiting']} {slow['aspect']} natal {slow['natal_planet']}...")
            text = build_slow_transit_interpretation(slow)
            slow_texts.append(text)
            slow["interpretation"] = text

        # Daily synthesis
        print(f"    Synthesis...")
        day["synthesis"] = build_daily_synthesis(day, asp_texts, slow_texts)

    return cycle_data

# ── PDF builder ────────────────────────────────────────────────────────────────
W, H = letter

CREAM        = colors.HexColor("#FAF8F4")
CREAM2       = colors.HexColor("#F0EDE7")
INK          = colors.HexColor("#2C2A26")
INK_MED      = colors.HexColor("#5A5855")
INK_LIGHT    = colors.HexColor("#9A9892")
BORDER       = colors.HexColor("#D3D1C7")
GOLD         = colors.HexColor("#BA7517")
GOLD_LIGHT   = colors.HexColor("#FDF0D5")
ROSE         = colors.HexColor("#8B3418")
ROSE_LIGHT   = colors.HexColor("#FAECE7")
TEAL         = colors.HexColor("#085041")
TEAL_LIGHT   = colors.HexColor("#DFF4EC")
PURPLE       = colors.HexColor("#3C3489")
PURPLE_LIGHT = colors.HexColor("#EEEDFE")
BLUE         = colors.HexColor("#0C447C")
BLUE_LIGHT   = colors.HexColor("#E6F1FB")
RED_DOT      = colors.HexColor("#C44030")
GREEN_DOT    = colors.HexColor("#1D8C62")
PURPLE_DOT   = colors.HexColor("#5B52C4")
GOLD_DOT     = colors.HexColor("#9A6010")

SIGN_COLORS = {
    "Aries":("FAECE7","8B3418"), "Taurus":("DFF4EC","085041"),
    "Gemini":("FDF0D5","8A5A10"), "Cancer":("E6F1FB","0C447C"),
    "Leo":("FDF0D5","5A3206"), "Virgo":("DFF4EC","085041"),
    "Libra":("EEEDFE","3C3489"), "Scorpio":("FAECE7","8B3418"),
    "Sagittarius":("FDF0D5","8A5A10"), "Capricorn":("EEEAE4","4A4844"),
    "Aquarius":("E6F1FB","0C447C"), "Pisces":("EEEDFE","3C3489"),
}

PHASE_META = {
    "FULL MOON":     {"bg":ROSE_LIGHT,   "fg":ROSE,   "bar":"#C44030"},
    "NEW MOON":      {"bg":PURPLE_LIGHT, "fg":PURPLE, "bar":"#6B60C8"},
    "FIRST QUARTER": {"bg":TEAL_LIGHT,   "fg":TEAL,   "bar":"#1D9E75"},
    "LAST QUARTER":  {"bg":GOLD_LIGHT,   "fg":GOLD,   "bar":"#BA7517"},
}

def sign_colors(sign):
    pair = SIGN_COLORS.get(sign, ("F0EDE7","5A5855"))
    return colors.HexColor("#"+pair[0]), colors.HexColor("#"+pair[1])

def asp_dot_color(aspect):
    if aspect in ("Conjunction","Opposition"): return RED_DOT
    if aspect in ("Trine","Sextile"):          return GREEN_DOT
    if aspect == "Square":                      return RED_DOT
    return PURPLE_DOT

def pill(c, x, y, w, h, bg, fg, text, fsize=5.5, bold=False):
    c.setFillColor(bg)
    c.roundRect(x, y, w, h, h/2, fill=1, stroke=0)
    c.setFillColor(fg)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", fsize)
    c.drawCentredString(x+w/2, y+h/2-fsize*0.36, text)

def wrap_draw(c, text, x, y, max_w, font, fsize, leading):
    c.setFont(font, fsize)
    for word_chunk in text.split("\n"):
        words = word_chunk.split()
        line = ""
        for w in words:
            test = (line+" "+w).strip()
            if c.stringWidth(test, font, fsize) > max_w:
                if line:
                    c.drawString(x, y, line)
                    y -= leading
                line = w
            else:
                line = test
        if line:
            c.drawString(x, y, line)
            y -= leading
    return y

def draw_cell(c, x, y, cw, ch, day):
    key = day["key_event"]
    if key and key in PHASE_META:
        bar_col = colors.HexColor(PHASE_META[key]["bar"])
        c.setFillColor(bar_col)
        c.rect(x, y+ch-3, cw, 3, fill=1, stroke=0)
        ih = ch-3
    else:
        ih = ch

    c.setFillColor(CREAM)
    c.rect(x, y, cw, ih, fill=1, stroke=0)
    c.setStrokeColor(BORDER); c.setLineWidth(0.3)
    c.rect(x, y, cw, ch, fill=0, stroke=1)

    pad = 3.2; top = y+ch-3.5
    dn = int(day["date"].split("-")[2])
    ms_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
              7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    ms = ms_map[int(day["date"].split("-")[1])]

    c.setFillColor(INK); c.setFont("Helvetica-Bold",8)
    c.drawString(x+pad, top-8, str(dn))
    c.setFillColor(INK_LIGHT); c.setFont("Helvetica",5)
    c.drawString(x+pad+13, top-7.5, ms)

    sign = day["moon_sign"]
    bg_s, fg_s = sign_colors(sign)
    deg = int(day["moon_deg"])
    pill(c, x+cw-28-pad, top-11, 27, 9, bg_s, fg_s, f"{deg}°{sign[:3]}", fsize=5)

    psh = day["phase_name"].replace("Waxing ","wx ").replace("Waning ","wn ")\
         .replace("Crescent","cres").replace("Gibbous","gib").replace("Quarter","Qtr")
    c.setFillColor(INK_MED); c.setFont("Helvetica",5)
    c.drawString(x+pad, top-19, psh)

    if key and key in PHASE_META:
        km = PHASE_META[key]
        ks = key.replace(" MOON","").replace(" QUARTER"," Q")
        pill(c, x+pad, top-29, 38, 8, km["bg"], km["fg"], ks, fsize=5)
        ay = top-39
    else:
        ay = top-27

    for asp in day["aspects"][:3]:
        if ay < y+18: break
        dc = asp_dot_color(asp["aspect"])
        c.setFillColor(dc); c.circle(x+pad+2, ay+1.5, 2, fill=1, stroke=0)
        c.setFillColor(INK_MED); c.setFont("Helvetica",4.7)
        ab = asp["aspect"][:3].lower()
        label = f"{ab} {asp['natal_planet'].replace('NNode','NN')} {asp['orb']:.2f}°"
        c.drawString(x+pad+6, ay, label)
        ay -= 7.5

def draw_calendar_page(c, cycle_data, year, month):
    c.setFillColor(CREAM); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(INK); c.rect(0,H-0.62*inch,W,0.62*inch,fill=1,stroke=0)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold",15)
    c.drawString(0.36*inch, H-0.36*inch, "Seraphe · Lunar Transit Calendar")
    ms_names = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
                7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
    c.setFont("Helvetica",8.5); c.setFillColor(colors.HexColor("#B0AEA8"))
    start_date = cycle_data[0]["date"]
    end_date = cycle_data[-1]["date"]
    c.drawString(0.36*inch, H-0.52*inch,
        f"Moon transits against natal chart  ·  {start_date} – {end_date}  ·  Exact orbs  ·  Personalized via Ollama")

    # Legend
    ly = H-0.80*inch
    c.setFont("Helvetica",6); c.setFillColor(INK_MED)
    c.drawString(0.36*inch, ly, "Phase events:")
    lx = 0.90*inch
    for key, meta in PHASE_META.items():
        short = key.replace(" MOON","").replace(" QUARTER"," Q")
        pill(c, lx, ly-2, 42, 9, meta["bg"], meta["fg"], short, fsize=5.5)
        lx += 46
    c.drawString(lx+4, ly, "Aspects:")
    lx += 50
    for col, lbl in [(GREEN_DOT,"tri/sxt"),(RED_DOT,"cnj/opp/sqr"),(PURPLE_DOT,"harmonic")]:
        c.setFillColor(col); c.circle(lx+3, ly+3, 3, fill=1, stroke=0)
        c.setFillColor(INK_MED); c.setFont("Helvetica",6)
        c.drawString(lx+8, ly, lbl); lx += 44

    # Grid
    gx = 0.27*inch; gtop = H-0.97*inch
    cw = (W-0.54*inch)/7; ch = (H-1.50*inch)/5
    DAYS = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
    c.setFillColor(INK); c.rect(gx, gtop-0.19*inch, 7*cw, 0.19*inch, fill=1, stroke=0)
    for i, d in enumerate(DAYS):
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold",6.5)
        c.drawCentredString(gx+i*cw+cw/2, gtop-0.13*inch, d.upper())

    # Determine start column from first day
    first_date = date.fromisoformat(cycle_data[0]["date"])
    start_col = first_date.weekday() + 1  # Monday=0 -> col 1; Sunday=6 -> col 0
    if start_col == 7: start_col = 0

    for idx, day in enumerate(cycle_data):
        ac = (start_col + idx) % 7
        row = (start_col + idx) // 7
        cx = gx + ac*cw; cy = gtop - 0.19*inch - (row+1)*ch
        draw_cell(c, cx, cy, cw, ch, day)

    # Empty leading cells
    for i in range(start_col):
        cx = gx + i*cw; cy = gtop - 0.19*inch - ch
        c.setFillColor(CREAM2); c.rect(cx, cy, cw, ch, fill=1, stroke=0)
        c.setStrokeColor(BORDER); c.setLineWidth(0.3)
        c.rect(cx, cy, cw, ch, fill=0, stroke=1)

    # Trailing empties
    total = start_col + len(cycle_data)
    trail = (7 - total % 7) % 7
    for i in range(trail):
        ac = (total+i)%7; row = (total+i)//7
        cx = gx+ac*cw; cy = gtop-0.19*inch-(row+1)*ch
        c.setFillColor(CREAM2); c.rect(cx,cy,cw,ch,fill=1,stroke=0)
        c.setStrokeColor(BORDER); c.setLineWidth(0.3); c.rect(cx,cy,cw,ch,fill=0,stroke=1)

    c.setFillColor(INK_LIGHT); c.setFont("Helvetica",5.5)
    c.drawCentredString(W/2, 0.13*inch,
        "Natal: Sun 26°23' Leo H9 · Moon 14°44' Pis H4 · ASC 26°15' Sco · MC 11°15' Vir · "
        "Venus 12°10' Lib H10 · Mars 9°38' Lib H10 · Jupiter 26°40' Can H8 · "
        "Saturn 2°58' Vir H9 · Uranus 12°41' Sco H12 · Neptune 15°33' Sag H1 · "
        "Pluto 14°45' Lib H11 · Lilith 23°58' Can H8 · NNode 26°57' Vir H10")

def draw_daily_page(c, day):
    c.setFillColor(CREAM); c.rect(0,0,W,H,fill=1,stroke=0)
    key = day["key_event"]
    bar_col = colors.HexColor(PHASE_META[key]["bar"]) if key and key in PHASE_META else INK
    c.setFillColor(bar_col); c.rect(0, H-0.58*inch, W, 0.58*inch, fill=1, stroke=0)

    dn = int(day["date"].split("-")[2])
    ms_map = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
              7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
    ms = ms_map[int(day["date"].split("-")[1])]
    yr = day["date"].split("-")[0]
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold",18)
    c.drawString(0.4*inch, H-0.36*inch, f"{day['dow']}, {ms} {dn}, {yr}")
    c.setFont("Helvetica",9); c.setFillColor(colors.HexColor("#D0CEC8"))
    c.drawRightString(W-0.4*inch, H-0.25*inch,
        f"Moon {day['moon_deg_str']}  ·  {day['phase_name']}")
    if key:
        c.setFont("Helvetica-Bold",9)
        c.drawRightString(W-0.4*inch, H-0.40*inch, key)

    lx = 0.4*inch; rw = W-0.8*inch; y = H-0.75*inch

    # Overall energy
    c.setFillColor(INK); c.setFont("Helvetica-Bold",8.5)
    c.drawString(lx, y, "Overall Energy"); y -= 0.12*inch
    c.setStrokeColor(GOLD); c.setLineWidth(0.6); c.line(lx,y,lx+rw,y); y -= 0.14*inch
    synthesis = day.get("synthesis","")
    if synthesis:
        c.setFillColor(INK); c.setFont("Helvetica",8)
        y = wrap_draw(c, synthesis, lx, y, rw, "Helvetica", 8, 11)
        y -= 0.08*inch

    # Aspects
    if day["aspects"]:
        c.setFillColor(INK); c.setFont("Helvetica-Bold",8.5)
        c.drawString(lx, y, "Moon Aspects to Natal Chart — Exact Orbs")
        y -= 0.12*inch
        c.setStrokeColor(GOLD); c.setLineWidth(0.6); c.line(lx,y,lx+rw,y); y -= 0.15*inch

        for asp in day["aspects"]:
            if y < 1.3*inch: break
            dc = asp_dot_color(asp["aspect"])
            c.setFillColor(dc); c.circle(lx+4, y+4, 4, fill=1, stroke=0)
            c.setFillColor(INK); c.setFont("Helvetica-Bold",8.5)
            nat = asp["natal_planet"]
            nat_info = SERAPHE_NATAL.get(nat, {})
            rx_str = " Rx" if nat_info.get("rx") else ""
            ndeg = f"{nat_info.get('deg','')} {nat_info.get('sign','')}{rx_str} H{nat_info.get('house','')}"
            header = f"Moon {asp['aspect']}  natal {nat}  —  {asp['orb']:.2f}° orb"
            c.drawString(lx+12, y+1, header)
            c.setFillColor(INK_LIGHT); c.setFont("Helvetica",7)
            c.drawRightString(W-0.4*inch, y+1, ndeg)
            y -= 0.14*inch

            interp = asp.get("interpretation","")
            if interp:
                c.setFillColor(INK_MED); c.setFont("Helvetica",7.5)
                y = wrap_draw(c, interp, lx+10, y, rw-14, "Helvetica", 7.5, 10)

            y -= 0.08*inch
            c.setStrokeColor(BORDER); c.setLineWidth(0.3)
            c.line(lx+6, y+4, lx+rw, y+4); y -= 0.06*inch

    elif not day["slow"]:
        ptext = f"No direct lunar-natal contacts today. Moon in {day['moon_sign']} — {day['phase_name']}."
        c.setFillColor(INK_MED); c.setFont("Helvetica",8)
        c.drawString(lx, y, ptext); y -= 0.15*inch

    # Slow transits
    if day["slow"] and y > 1.3*inch:
        c.setFillColor(INK); c.setFont("Helvetica-Bold",8.5)
        c.drawString(lx, y, "Slower Planet Transits Active"); y -= 0.12*inch
        c.setStrokeColor(PURPLE_DOT); c.setLineWidth(0.6); c.line(lx,y,lx+rw,y); y -= 0.15*inch

        for sl in day["slow"]:
            if y < 1.0*inch: break
            c.setFillColor(PURPLE_DOT); c.circle(lx+4, y+4, 3.5, fill=1, stroke=0)
            c.setFillColor(INK); c.setFont("Helvetica-Bold",8)
            nat_info = SERAPHE_NATAL.get(sl["natal_planet"],{})
            header = (f"Transit {sl['transiting']} {sl['transiting_deg']}  "
                      f"{sl['aspect']} natal {sl['natal_planet']}  —  {sl['orb']:.2f}° orb")
            c.drawString(lx+11, y+1, header); y -= 0.13*inch
            interp = sl.get("interpretation","")
            if interp:
                c.setFillColor(INK_MED); c.setFont("Helvetica",7.5)
                y = wrap_draw(c, interp, lx+10, y, rw-14, "Helvetica", 7.5, 10)
            y -= 0.08*inch
            c.setStrokeColor(BORDER); c.setLineWidth(0.3)
            c.line(lx+6, y+4, lx+rw, y+4); y -= 0.06*inch

    # Footer
    c.setFillColor(BORDER); c.setLineWidth(0.3)
    c.line(0.4*inch, 0.22*inch, W-0.4*inch, 0.22*inch)
    c.setFillColor(INK_LIGHT); c.setFont("Helvetica",5.5)
    c.drawString(0.4*inch, 0.12*inch, "Seraphe Valemira · Lunar Transit Calendar · Mythos")
    c.drawRightString(W-0.4*inch, 0.12*inch,
        f"{day['date']} · Moon {day['moon_deg_str']} · {day['phase_name']}")

def draw_reference_page(c):
    c.setFillColor(CREAM); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(INK); c.rect(0,H-0.5*inch,W,0.5*inch,fill=1,stroke=0)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold",13)
    c.drawString(0.4*inch, H-0.31*inch, "Seraphe · Natal Chart Reference")

    lx = 0.4*inch; rw = W-0.8*inch; y = H-0.70*inch
    c.setFillColor(INK); c.setFont("Helvetica-Bold",9)
    c.drawString(lx, y, "Natal Placements"); y -= 0.12*inch
    c.setStrokeColor(GOLD); c.setLineWidth(0.7); c.line(lx,y,lx+rw,y); y -= 0.13*inch

    col1x = lx; col2x = lx+rw/2+0.05*inch; colw = rw/2-0.05*inch
    c1y = y; c2y = y

    items = list(SERAPHE_NATAL.items())
    half = len(items)//2
    for i, (planet, info) in enumerate(items):
        cx = col1x if i < half else col2x
        cy_ref = c1y if i < half else c2y
        dg = info.get("dig","") or ""
        rx_s = " Rx" if info.get("rx") else ""
        sign_s = info.get("sign","")
        deg_s = info.get("deg","")
        house_s = f"H{info.get('house','')}" if info.get("house") else ""
        desc_s = info.get("desc","")

        c.setFillColor(INK); c.setFont("Helvetica-Bold",7)
        c.drawString(cx, cy_ref, f"{planet}  {deg_s} {sign_s}{rx_s}  {house_s}")
        if i < half: c1y -= 9
        else:        c2y -= 9

        c.setFillColor(INK_MED); c.setFont("Helvetica",6.5)
        words = desc_s.split()
        line = ""
        ref_y = c1y if i < half else c2y
        for w in words:
            test = (line+" "+w).strip()
            if c.stringWidth(test,"Helvetica",6.5) > colw-8:
                c.drawString(cx+6, ref_y, line); ref_y -= 8; line = w
            else: line = test
        if line: c.drawString(cx+6, ref_y, line); ref_y -= 8
        ref_y -= 5
        if i < half: c1y = ref_y
        else:        c2y = ref_y

    c.setFillColor(INK_LIGHT); c.setFont("Helvetica",5.5)
    c.drawCentredString(W/2, 0.13*inch,
        "Seraphe Valemira · Lunar Transit Calendar · Mythos / Sovereign Consulting")

def build_pdf(cycle_data, out_path):
    """Assemble the full PDF from enriched cycle data."""
    year = int(cycle_data[0]["date"].split("-")[0])
    month = int(cycle_data[0]["date"].split("-")[1])

    c = rl_canvas.Canvas(str(out_path), pagesize=letter)
    c.setTitle(f"Seraphe · Lunar Transit Calendar {cycle_data[0]['date']} – {cycle_data[-1]['date']}")
    c.setAuthor("Ka'tuar'el / Mythos SEN-0001")

    # Page 1: calendar grid
    draw_calendar_page(c, cycle_data, year, month)
    c.showPage()

    # One page per day
    for day in cycle_data:
        draw_daily_page(c, day)
        c.showPage()

    # Reference page
    draw_reference_page(c)

    c.save()
    print(f"  PDF saved: {out_path}")

# ── Main entry point ───────────────────────────────────────────────────────────
def run(year=None, month=None, skip_ollama=False, out_path=None):
    if year is None or month is None:
        today = date.today()
        year = today.year
        month = today.month

    print(f"\nSeraphe Lunar Calendar Generator — {year}/{month:02d}")
    print(f"  Finding lunar cycle start...")
    days = get_cycle_days(year, month)
    start = days[0]; end = days[-1]
    print(f"  Cycle: {start} → {end} ({len(days)} days)")

    print(f"  Computing daily transits...")
    cycle_data = [compute_day(d) for d in days]

    # Assign key events — single closest day per peak, no duplicates
    cycle_data = assign_key_events(cycle_data)

    # Report what was found
    total_aspects = sum(len(d["aspects"]) for d in cycle_data)
    total_slow = sum(len(d["slow"]) for d in cycle_data)
    key_days = [d for d in cycle_data if d["key_event"]]
    print(f"  Found {total_aspects} lunar-natal aspects, {total_slow} slow transit hits")
    print(f"  Key events: {', '.join(d['date']+' '+d['key_event'] for d in key_days)}")

    if not skip_ollama:
        print(f"  Generating personalized interpretations via Ollama ({OLLAMA_MODEL})...")
        cycle_data = generate_interpretations(cycle_data)
    else:
        print("  [Skipping Ollama — using rich stub interpretations]")
        for day in cycle_data:
            for asp in day["aspects"]:
                nat_info = SERAPHE_NATAL.get(asp["natal_planet"], {})
                desc = nat_info.get("desc", "")
                asp["interpretation"] = (
                    f"Moon {asp['aspect']} natal {asp['natal_planet']} "
                    f"({asp['orb']:.2f}° orb) — {desc}"
                )
            for sl in day["slow"]:
                nat_info = SERAPHE_NATAL.get(sl["natal_planet"], {})
                desc = nat_info.get("desc", "")
                sl["interpretation"] = (
                    f"Transit {sl['transiting']} at {sl['transiting_deg']} "
                    f"{sl['aspect']} natal {sl['natal_planet']} ({sl['orb']:.2f}° orb) — {desc}"
                )
            day["synthesis"] = build_stub_synthesis(day)

    if out_path is None:
        fname = f"Seraphe_Lunar_{year}_{month:02d}.pdf"
        out_path = OUTPUT_DIR / fname

    print(f"  Building PDF...")
    build_pdf(cycle_data, out_path)

    # Save JSON alongside PDF for reference/caching
    json_path = out_path.with_suffix(".json")
    with open(json_path, "w") as f:
        json.dump(cycle_data, f, indent=2, default=str)
    print(f"  JSON saved: {json_path}")

    return str(out_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seraphe Lunar Calendar Generator")
    parser.add_argument("--year",  type=int, help="Year (default: current)")
    parser.add_argument("--month", type=int, help="Month 1-12 (default: current)")
    parser.add_argument("--skip-ollama", action="store_true",
                        help="Skip Ollama calls (stub interpretations — fast, for testing)")
    parser.add_argument("--out", type=str, help="Override output path")
    args = parser.parse_args()

    out = run(
        year=args.year,
        month=args.month,
        skip_ollama=args.skip_ollama,
        out_path=Path(args.out) if args.out else None,
    )
    print(f"\nDone: {out}")

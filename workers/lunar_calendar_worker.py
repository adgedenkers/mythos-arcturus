"""
Lunar Calendar Scheduler Worker — SEN-0001
/opt/mythos/workers/lunar_calendar_worker.py

Runs as a long-lived background process (mythos-worker-lunar.service).
Polls for new moon events and auto-generates Seraphe's calendar
for the upcoming cycle. Sends a Telegram notification when ready.

Architecture follows temporal_worker.py pattern.
"""

import os
import sys
import time
import logging
import subprocess
import requests
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, "/opt/mythos")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [lunar_worker] %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/opt/mythos/logs/lunar_calendar_worker.log"),
    ]
)
log = logging.getLogger("lunar_worker")

try:
    import swisseph as swe
    EPHE_PATH = "/opt/mythos/ephemeris/ephe"
    if os.path.isdir(EPHE_PATH):
        swe.set_ephe_path(EPHE_PATH)
except ImportError:
    log.error("pyswisseph not available")
    sys.exit(1)

GENERATOR = "/opt/mythos/astrology/seraphe_lunar_generator.py"
VENV_PYTHON = "/opt/mythos/.venv/bin/python3"
OUTPUT_DIR = Path("/opt/mythos/outputs/lunar_calendars")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load Telegram config from environment or config file
def get_telegram_config():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")  # Adge's chat
    seraphe_id = "8069190169"  # Seraphe's Telegram ID

    if not token:
        # Try loading from config
        config_path = Path("/opt/mythos/config/telegram.conf")
        if config_path.exists():
            with open(config_path) as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        if k.strip() == "BOT_TOKEN":
                            token = v.strip()
                        elif k.strip() == "CHAT_ID":
                            chat_id = v.strip()
    return token, chat_id, seraphe_id

def send_telegram(token, chat_id, text):
    if not token or not chat_id:
        log.warning("Telegram not configured — skipping notification")
        return
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=15,
        )
        if resp.status_code == 200:
            log.info(f"Telegram notification sent to {chat_id}")
        else:
            log.warning(f"Telegram send failed: {resp.text[:200]}")
    except Exception as e:
        log.error(f"Telegram error: {e}")

def moon_phase_angle(jd_val):
    m, _ = swe.calc_ut(jd_val, swe.MOON)
    s, _ = swe.calc_ut(jd_val, swe.SUN)
    return (m[0] - s[0]) % 360

def is_new_moon_today():
    """Returns True if today is within 12 hours of a new moon."""
    today = date.today()
    jd_val = swe.julday(today.year, today.month, today.day, 12.0)
    ang = moon_phase_angle(jd_val)
    return ang < 15 or ang > 345

def next_month(year, month):
    if month == 12:
        return year + 1, 1
    return year, month + 1

def calendar_exists(year, month):
    fname = f"Seraphe_Lunar_{year}_{month:02d}.pdf"
    return (OUTPUT_DIR / fname).exists()

def generate_calendar(year, month):
    log.info(f"Generating calendar for {year}/{month:02d}...")
    cmd = [VENV_PYTHON, GENERATOR, "--year", str(year), "--month", str(month)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            log.info(f"Calendar generated successfully for {year}/{month:02d}")
            return True, None
        else:
            err = result.stderr[-300:] if result.stderr else "Unknown error"
            log.error(f"Generator failed: {err}")
            return False, err
    except subprocess.TimeoutExpired:
        log.error("Generator timed out")
        return False, "Timeout"
    except Exception as e:
        log.error(f"Generator exception: {e}")
        return False, str(e)

def run():
    log.info("Lunar calendar worker starting")
    token, chat_id, seraphe_id = get_telegram_config()

    # Track last check to avoid re-triggering on same new moon
    last_generated_key = None
    check_interval = 3600  # Check every hour

    while True:
        try:
            today = date.today()

            if is_new_moon_today():
                # Generate next month's calendar
                ny, nm = next_month(today.year, today.month)
                gen_key = f"{ny}-{nm:02d}"

                if gen_key != last_generated_key:
                    log.info(f"New moon detected — generating calendar for {gen_key}")

                    if calendar_exists(ny, nm):
                        log.info(f"Calendar for {gen_key} already exists — skipping")
                        last_generated_key = gen_key
                    else:
                        success, err = generate_calendar(ny, nm)
                        last_generated_key = gen_key

                        if success:
                            fname = f"Seraphe_Lunar_{ny}_{nm:02d}.pdf"
                            fpath = OUTPUT_DIR / fname
                            month_names = ["","January","February","March","April","May","June",
                                           "July","August","September","October","November","December"]
                            msg = (
                                f"🌑 *New Moon — Seraphe's lunar calendar is ready*\n\n"
                                f"*{month_names[nm]} {ny}* lunar transit calendar has been generated.\n"
                                f"File: `{fpath}`\n\n"
                                f"One page per day, personalized interpretations for each aspect to Seraphe's natal chart."
                            )
                            send_telegram(token, chat_id, msg)
                        else:
                            msg = f"⚠️ Lunar calendar generation failed for {gen_key}: {err}"
                            send_telegram(token, chat_id, msg)

            # Also check: ensure current month's calendar exists
            cur_key = f"{today.year}-{today.month:02d}"
            if not calendar_exists(today.year, today.month):
                log.info(f"Current month calendar missing — generating {cur_key}")
                success, err = generate_calendar(today.year, today.month)
                if success:
                    log.info(f"Backfilled calendar for {cur_key}")
                else:
                    log.error(f"Backfill failed for {cur_key}: {err}")

        except Exception as e:
            log.error(f"Worker loop error: {e}")

        time.sleep(check_interval)

if __name__ == "__main__":
    run()

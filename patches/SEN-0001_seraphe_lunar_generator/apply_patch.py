import sys
import os
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SEN',
    number=1,
    description='seraphe_lunar_generator',
    patch_type='MAJOR',
)
patch.begin()

# ── Create output directory ────────────────────────────────────────────────────
os.makedirs('/opt/mythos/outputs/lunar_calendars', exist_ok=True)
os.makedirs('/opt/mythos/logs', exist_ok=True)

# ── Deploy core generator ──────────────────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/astrology/seraphe_lunar_generator.py',
    '/opt/mythos/astrology/seraphe_lunar_generator.py'
)

# ── Deploy skill ───────────────────────────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/skills/data/lunar_calendar_skill.py',
    '/opt/mythos/skills/data/lunar_calendar_skill.py'
)

# ── Deploy worker ──────────────────────────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/workers/lunar_calendar_worker.py',
    '/opt/mythos/workers/lunar_calendar_worker.py'
)

# ── Deploy CLI script (make executable) ───────────────────────────────────────
patch.deploy_file(
    'opt/mythos/bin/seraphe-lunar',
    '/opt/mythos/bin/seraphe-lunar'
)
os.chmod('/opt/mythos/bin/seraphe-lunar', 0o755)

# ── Deploy systemd service ─────────────────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/services/mythos-worker-lunar.service',
    '/opt/mythos/services/mythos-worker-lunar.service'
)

# Install and enable service
subprocess.run([
    'sudo', 'cp',
    '/opt/mythos/services/mythos-worker-lunar.service',
    '/etc/systemd/system/mythos-worker-lunar.service'
], check=True)
subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
subprocess.run(['sudo', 'systemctl', 'enable', 'mythos-worker-lunar.service'], check=True)
subprocess.run(['sudo', 'systemctl', 'start',  'mythos-worker-lunar.service'], check=True)

# ── Ensure reportlab is installed ─────────────────────────────────────────────
try:
    import reportlab
    print("  reportlab already installed")
except ImportError:
    print("  Installing reportlab...")
    subprocess.run([
        '/opt/mythos/.venv/bin/pip', 'install', 'reportlab', '--quiet'
    ], check=True)
    print("  reportlab installed")

# ── Restart bot to pick up new skill ──────────────────────────────────────────
patch.restart_service('mythos-bot.service')

patch.finish()

print("""
╔══════════════════════════════════════════════════════════════╗
║  SEN-0001  Seraphe Lunar Generator — Installed               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  CLI:     seraphe-lunar                                      ║
║           seraphe-lunar --year 2026 --month 6               ║
║           seraphe-lunar --skip-ollama  (fast/test mode)     ║
║           seraphe-lunar --list                               ║
║           seraphe-lunar --status                             ║
║                                                              ║
║  Iris:    "generate lunar calendar"                         ║
║           "lunar calendar for May"                           ║
║           "seraphe lunar calendar june 2026"                 ║
║                                                              ║
║  Auto:    Worker fires on each new moon                      ║
║           Generates next month's calendar automatically      ║
║           mythos-worker-lunar.service                        ║
║                                                              ║
║  Output:  /opt/mythos/outputs/lunar_calendars/               ║
║           Seraphe_Lunar_YYYY_MM.pdf                          ║
║           Seraphe_Lunar_YYYY_MM.json  (cache/debug)          ║
║                                                              ║
║  Pages:   1 calendar grid + 1 per day + natal reference      ║
║  AI:      qwen2.5:32b via Ollama — personalized per aspect   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

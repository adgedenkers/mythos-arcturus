import sys
import os
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=44,
    description='Denkers Co public website - static hosting via systemd + tunnel',
    patch_type='MINOR',
)
patch.begin()

# ── 1. Deploy systemd service ──
service_src = os.path.join(os.path.dirname(__file__), 'denkers-web.service')
service_dst = '/etc/systemd/system/denkers-web.service'

print("[1/4] Installing denkers-web.service...")
subprocess.run(['sudo', 'cp', service_src, service_dst], check=True)
subprocess.run(['sudo', 'chmod', '644', service_dst], check=True)
subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
subprocess.run(['sudo', 'systemctl', 'enable', 'denkers-web.service'], check=True)
subprocess.run(['sudo', 'systemctl', 'start', 'denkers-web.service'], check=True)
print("  ✓ denkers-web.service installed and started on port 8090")

# ── 2. Update Cloudflare tunnel config ──
print("[2/4] Updating Cloudflare tunnel config...")
tunnel_src = os.path.join(os.path.dirname(__file__), 'cloudflared-config.yml')
tunnel_dst = '/etc/cloudflared/config.yml'

# Back up existing config
subprocess.run(['sudo', 'cp', tunnel_dst, tunnel_dst + '.bak.sys0044'], check=True)
subprocess.run(['sudo', 'cp', tunnel_src, tunnel_dst], check=True)
print("  ✓ Tunnel config updated (backup at config.yml.bak.sys0044)")

# ── 3. Restart cloudflared ──
print("[3/4] Restarting cloudflared...")
subprocess.run(['sudo', 'systemctl', 'restart', 'cloudflared'], check=True)
print("  ✓ cloudflared restarted")

# ── 4. Verify ──
print("[4/4] Verifying...")
import time
time.sleep(2)

result = subprocess.run(
    ['ss', '-tlnp'],
    capture_output=True, text=True
)
if ':8090' in result.stdout:
    print("  ✓ Port 8090 listening")
else:
    print("  ⚠ Port 8090 not detected — check: sudo systemctl status denkers-web.service")

result = subprocess.run(
    ['sudo', 'systemctl', 'is-active', 'cloudflared'],
    capture_output=True, text=True
)
if 'active' in result.stdout:
    print("  ✓ cloudflared running")
else:
    print("  ⚠ cloudflared may not be running — check: sudo systemctl status cloudflared")

print()
print("=" * 50)
print("  SYS-0044 Complete")
print("=" * 50)
print()
print("  Site serving from: /opt/mythos/web/denkers-site/")
print("  Local: http://127.0.0.1:8090")
print("  Public: https://denkers.co (after DNS update)")
print()
print("  MANUAL STEP REQUIRED:")
print("  In Cloudflare DNS (dash.cloudflare.com):")
print("  1. Delete the two A records for denkers.co")
print("  2. Add CNAME: denkers.co → f40f4018-7b7d-412a-900e-5b8b5433394c.cfargotunnel.com (proxied)")
print("  3. Verify www.denkers.co already CNAMEs to denkers.co")
print()

patch.finish()

import sys
import os
import subprocess
import json
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=43,
    description='homebridge vizio smartcast siri control',
    patch_type='MINOR',
)
patch.begin()

def run(cmd, check=True, capture=True):
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if check and result.returncode != 0:
        print(f"  [!] Error: {result.stderr[:300]}")
        raise RuntimeError(f"Command failed: {cmd}")
    if capture and result.stdout.strip():
        print(f"  {result.stdout.strip()[:200]}")
    return result

# 1. Install Node.js if not present
result = run('which node', check=False)
if result.returncode != 0:
    print("Installing Node.js...")
    run('curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -', capture=False)
    run('sudo apt-get install -y nodejs', capture=False)
else:
    print(f"✓ Node.js already installed: {result.stdout.strip()}")

# 2. Install Homebridge globally
result = run('which homebridge', check=False)
if result.returncode != 0:
    print("Installing Homebridge...")
    run('sudo npm install -g --unsafe-perm homebridge homebridge-config-ui-x', capture=False)
else:
    print("✓ Homebridge already installed")

# 3. Install homebridge-vizio-smartcast plugin
print("Installing homebridge-vizio-smartcast plugin...")
run('sudo npm install -g homebridge-vizio-smartcast', capture=False)

# 4. Create Homebridge config directory
hb_dir = '/var/lib/homebridge'
run(f'sudo mkdir -p {hb_dir}')
run(f'sudo chown -R adge:adge {hb_dir}')

# 5. Write initial Homebridge config
config = {
    "bridge": {
        "name": "Arcturus Bridge",
        "username": "CC:22:3D:E3:CE:30",
        "port": 51826,
        "pin": "031-45-154"
    },
    "description": "Mythos Homebridge on Arcturus",
    "accessories": [],
    "platforms": [
        {
            "platform": "config",
            "name": "Config",
            "port": 8581
        }
    ]
}

config_path = f'{hb_dir}/config.json'
if not os.path.exists(config_path):
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"✓ Created {config_path}")
else:
    print(f"✓ Config already exists at {config_path} — not overwriting")

# 6. Create systemd service
service_content = """[Unit]
Description=Homebridge — Mythos Smart Home Bridge
After=network-online.target

[Service]
Type=simple
User=adge
ExecStart=/usr/bin/homebridge -U /var/lib/homebridge
Restart=on-failure
RestartSec=10
KillMode=process

[Install]
WantedBy=multi-user.target
"""

service_path = '/etc/systemd/system/homebridge.service'
with open('/tmp/homebridge.service', 'w') as f:
    f.write(service_content)
run(f'sudo cp /tmp/homebridge.service {service_path}')
run('sudo systemctl daemon-reload')
run('sudo systemctl enable homebridge')
run('sudo systemctl start homebridge')
print("✓ Homebridge service installed and started")

print("\n" + "="*60)
print("Homebridge installed on Arcturus.")
print("")
print("Next steps to add your Vizio TV:")
print("")
print("1. Find your Vizio TV's local IP address (check router)")
print("")
print("2. Pair with the TV (run once from Arcturus):")
print("   node -e \"")
print("     const v = require('homebridge-vizio-smartcast');")
print("     // See pairing instructions below")
print("   \"")
print("")
print("3. Open Homebridge UI at:")
print("   http://arcturus-local-ip:8581")
print("   Default login: admin / admin")
print("")
print("4. Add Vizio accessory via UI using your TV's IP + auth token")
print("")
print("5. Open Apple Home app on iPhone → Add Accessory")
print("   → scan Homebridge QR code (pin: 031-45-154)")
print("")
print("6. Say: 'Hey Siri, turn on TV'")
print("="*60)

patch.finish()

import sys
import os
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=42,
    description='shell to telegram loop',
    patch_type='MINOR',
)
patch.begin()

# 1. Deploy the shell_result route
patch.deploy_file(
    'opt/mythos/api/routes/shell_result.py',
    '/opt/mythos/api/routes/shell_result.py'
)
print("✓ Deployed shell_result.py route")

# 2. Wire route into main.py
main_path = '/opt/mythos/api/main.py'
with open(main_path, 'r') as f:
    content = f.read()

if 'shell_result' not in content:
    # Find the last router import and add after it
    import_line = 'from api.routes.shell_result import router as shell_result_router'
    include_line = 'app.include_router(shell_result_router, prefix="/api")'

    # Add import — find a good anchor (finance router import is always present)
    old = 'from api.routes.finance import router as finance_router'
    new = f'{import_line}\n{old}'
    if old in content:
        content = content.replace(old, new, 1)

    # Add include — find anchor
    old2 = 'app.include_router(finance_router'
    new2 = f'{include_line}\n{old2}'
    if old2 in content:
        content = content.replace(old2, new2, 1)

    with open(main_path, 'w') as f:
        f.write(content)
    print("✓ Wired shell_result router into main.py")
else:
    print("✓ shell_result already in main.py — skipping")

# 3. Add SHELL_API_KEY and ADGE_TELEGRAM_ID to .env if missing
env_path = '/opt/mythos/.env'
with open(env_path, 'r') as f:
    env_content = f.read()

additions = []
if 'SHELL_API_KEY' not in env_content:
    import secrets
    key = secrets.token_hex(32)
    additions.append(f'SHELL_API_KEY={key}')
    print(f"✓ Generated SHELL_API_KEY — save this for your iOS Shortcut")

if 'ADGE_TELEGRAM_ID' not in env_content:
    additions.append('ADGE_TELEGRAM_ID=')
    print("⚠ ADGE_TELEGRAM_ID not set — add your Telegram user ID to .env")

if additions:
    with open(env_path, 'a') as f:
        f.write('\n# Shell-to-Telegram (SYS-0042)\n')
        for line in additions:
            f.write(line + '\n')

# 4. Restart API
patch.restart_service('mythos-api.service')
print("✓ mythos-api.service restarted")

print("\n" + "="*60)
print("Shell-to-Telegram endpoint live at:")
print("  POST https://mythos-api.denkers.co/api/shell-result")
print("  GET  https://mythos-api.denkers.co/api/shell-result/ping")
print("\nNext steps:")
print("  1. Add your Telegram user ID to ADGE_TELEGRAM_ID in .env")
print("  2. Copy SHELL_API_KEY from .env — you'll need it for the iOS Shortcut")
print("  3. Test: curl -X GET https://mythos-api.denkers.co/api/shell-result/ping")
print("="*60)

patch.finish()

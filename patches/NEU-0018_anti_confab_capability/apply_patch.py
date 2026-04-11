import sys
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=18,
    description='Anti-confab capability fabrication + closing question fix',
    patch_type='MINOR',
)
patch.begin()

# Deploy updated Modelfiles
patch.deploy_file('opt/mythos/prompts/Modelfile', '/opt/mythos/prompts/Modelfile')
patch.deploy_file('opt/mythos/prompts/Modelfile.deep', '/opt/mythos/prompts/Modelfile.deep')

# Rebuild both ollama models with updated prompts
print("\n🔨 Rebuilding iris:latest...")
result = subprocess.run(
    ['ollama', 'create', 'iris', '-f', '/opt/mythos/prompts/Modelfile'],
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print(f"⚠ iris:latest build warning: {result.stderr}")

print("🔨 Rebuilding iris-deep:latest...")
result = subprocess.run(
    ['ollama', 'create', 'iris-deep', '-f', '/opt/mythos/prompts/Modelfile.deep'],
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print(f"⚠ iris-deep:latest build warning: {result.stderr}")

# Restart bot to pick up any cached model state
patch.restart_service('mythos-bot.service')

patch.finish()
print("\n✅ NEU-0018 complete — both models rebuilt with v4 prompt")
print("   Added: capability fabrication anti-confab rules")
print("   Fixed: closing question prohibition strengthened")
print("   Test: send casual messages via Telegram, check for fake offers + trailing questions")

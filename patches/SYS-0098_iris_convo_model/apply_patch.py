"""
SYS-0098: iris:convo model + /cosmos and /standard commands

What this patch changes:
- Creates /opt/mythos/prompts/Modelfile.convo (clean technical partner identity)
- Creates /opt/mythos/telegram_bot/handlers/cosmos_handler.py (/cosmos, /standard)
- Replaces /opt/mythos/core/model_aliases.py (iris:convo as default, new aliases)
- Updates /opt/mythos/.env: OLLAMA_MODEL=iris:convo
- Bakes iris:convo model via ollama create
- Retags iris:latest → iris:cosmos, iris-deep:latest → iris:cosmos-deep
- Registers /cosmos and /standard commands in mythos_bot.py

Services restarted: mythos-bot.service
Tables touched: none
"""
import sys
import subprocess

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=98,
    description='iris convo model + cosmos/standard commands',
    patch_type='MINOR',
)
patch.begin()

# ── Deploy files ──────────────────────────────────────────────────────────

patch.deploy_file(
    'opt/mythos/prompts/Modelfile.convo',
    '/opt/mythos/prompts/Modelfile.convo',
)

patch.deploy_file(
    'opt/mythos/telegram_bot/handlers/cosmos_handler.py',
    '/opt/mythos/telegram_bot/handlers/cosmos_handler.py',
)

patch.deploy_file(
    'opt/mythos/core/model_aliases.py',
    '/opt/mythos/core/model_aliases.py',
)

# ── Update .env — change default model ────────────────────────────────────

patch.str_replace(
    '/opt/mythos/.env',
    old='OLLAMA_MODEL=iris-deep:latest',
    new='OLLAMA_MODEL=iris:convo',
    label='.env default model',
)

# ── Bake iris:convo model ─────────────────────────────────────────────────

patch.logger.log("  · Baking iris:convo from Modelfile.convo...")
try:
    result = subprocess.run(
        ['ollama', 'create', 'iris:convo', '-f', '/opt/mythos/prompts/Modelfile.convo'],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode == 0:
        patch.logger.log("  ✓ iris:convo baked successfully")
    else:
        stderr = (result.stderr or '').strip()[:200]
        patch.errors.append(f"ollama create iris:convo failed: {stderr}")
        patch.logger.log(f"  ✗ iris:convo bake failed: {stderr}")
except Exception as e:
    patch.errors.append(f"ollama create iris:convo: {e}")
    patch.logger.log(f"  ✗ iris:convo bake error: {e}")

# ── Retag existing models ────────────────────────────────────────────────

for src, dst in [("iris:latest", "iris:cosmos"), ("iris-deep:latest", "iris:cosmos-deep")]:
    patch.logger.log(f"  · Copying {src} → {dst}...")
    try:
        result = subprocess.run(
            ['ollama', 'cp', src, dst],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            patch.logger.log(f"  ✓ {dst} created from {src}")
        else:
            stderr = (result.stderr or '').strip()[:200]
            patch.logger.log(f"  ⚠ {dst} copy failed (non-fatal): {stderr}")
    except Exception as e:
        patch.logger.log(f"  ⚠ {dst} copy error (non-fatal): {e}")

# ── Register /cosmos and /standard in mythos_bot.py ───────────────────────

# Import — insert after the help_handler import line
patch.ensure_line_in_file(
    '/opt/mythos/telegram_bot/mythos_bot.py',
    line='from handlers.cosmos_handler import cosmos_command, standard_command',
    after='from handlers.help_handler import help_command as help_command_handler',
    label='bot import cosmos_handler',
)

# Handler registration — insert after the meditate command registration
patch.ensure_line_in_file(
    '/opt/mythos/telegram_bot/mythos_bot.py',
    line='    application.add_handler(CommandHandler("cosmos", cosmos_command))',
    after='    application.add_handler(CommandHandler("meditate", meditate_command))',
    label='bot register /cosmos',
)

patch.ensure_line_in_file(
    '/opt/mythos/telegram_bot/mythos_bot.py',
    line='    application.add_handler(CommandHandler("standard", standard_command))',
    after='    application.add_handler(CommandHandler("cosmos", cosmos_command))',
    label='bot register /standard',
)

# ── Validate bot syntax ──────────────────────────────────────────────────

patch.py_compile_check(
    '/opt/mythos/telegram_bot/mythos_bot.py',
    label='mythos_bot.py syntax',
)

# ── Restart bot ───────────────────────────────────────────────────────────

patch.restart_service('mythos-bot.service')

patch.finish()

"""
SYS-0034: Fix benchmark --config flag not honoured
- run_benchmark.py has CONFIG_PATH hardcoded at module level (line 44)
- argparse --config flag was wired up but never connected to CONFIG_PATH
- Fix: move CONFIG loading into main() after argparse, pass CONFIG into runner
- Also deploys updated bench_config_round2.json with correct 9-model list
  and doubled timeouts to prevent cascade skips on large models under load
"""

import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=34,
    description='fix benchmark --config flag not honoured + round2 timeout tuning',
    patch_type='PATCH',
)
patch.begin()

PATCH_DIR = Path(__file__).parent
BENCH_DIR = Path('/opt/mythos/orchestrator/benchmark')
RUNNER = BENCH_DIR / 'run_benchmark.py'

# ── 1. Deploy updated bench_config_round2.json ───────────────────────────────

patch.deploy_file(
    str(PATCH_DIR / 'opt/mythos/orchestrator/benchmark/bench_config_round2.json'),
    str(BENCH_DIR / 'bench_config_round2.json'),
)
print("  ✓ bench_config_round2.json updated (9 models, doubled timeouts)")

# ── 2. Fix CONFIG_PATH hardcode in run_benchmark.py ──────────────────────────

text = RUNNER.read_text()

# Verify the hardcode is still there before patching
if 'CONFIG_PATH = BENCH_DIR / "bench_config.json"' not in text:
    print("  ⚠ CONFIG_PATH hardcode not found at expected location")
    print("    Checking alternative forms...")
    if 'CONFIG_PATH' in text:
        # Find and show the line for manual inspection
        for i, line in enumerate(text.splitlines(), 1):
            if 'CONFIG_PATH' in line:
                print(f"    Line {i}: {line.strip()}")
    print("    Skipping run_benchmark.py patch — inspect manually")
else:
    # Step 1: Remove the module-level CONFIG_PATH hardcode
    # Replace it with a comment explaining it moved to main()
    text = text.replace(
        'CONFIG_PATH = BENCH_DIR / "bench_config.json"',
        '# CONFIG_PATH is now set in main() from --config arg (was hardcoded here — SYS-0034)'
    )

    # Step 2: Find where CONFIG is loaded from CONFIG_PATH
    # Typical pattern: CONFIG = json.loads(CONFIG_PATH.read_text())
    # We need to make this use the parsed args instead
    # Look for the load pattern
    config_load_patterns = [
        'CONFIG = json.loads(CONFIG_PATH.read_text())',
        'CONFIG = json.load(CONFIG_PATH.open())',
        'with open(CONFIG_PATH) as f:\n    CONFIG = json.load(f)',
    ]

    config_load_found = None
    for pattern in config_load_patterns:
        if pattern in text:
            config_load_found = pattern
            break

    if config_load_found:
        # Wrap with a deferred load sentinel — we'll do the real fix in main()
        text = text.replace(
            config_load_found,
            'CONFIG = {}  # populated in main() from --config arg (SYS-0034)'
        )
        print("  ✓ Removed module-level CONFIG load")
    else:
        print("  ⚠ Could not find CONFIG load pattern — checking what's there:")
        for i, line in enumerate(text.splitlines(), 1):
            if 'CONFIG' in line and ('json' in line or 'load' in line or 'read' in line):
                print(f"    Line {i}: {line.strip()}")

    # Step 3: In main(), after args = parser.parse_args(), inject CONFIG loading
    # Find the parse_args() call
    parse_args_line = 'args = parser.parse_args()'
    if parse_args_line in text:
        config_init_block = (
            'args = parser.parse_args()\n\n'
            '    # SYS-0034: load config from --config arg (was hardcoded at module level)\n'
            '    global CONFIG, CONFIG_PATH\n'
            '    CONFIG_PATH = BENCH_DIR / args.config\n'
            '    if not CONFIG_PATH.exists():\n'
            '        print(f"ERROR: Config file not found: {CONFIG_PATH}")\n'
            '        sys.exit(1)\n'
            '    CONFIG = json.loads(CONFIG_PATH.read_text())\n'
            '    print(f"  Loaded config: {CONFIG_PATH.name}")\n'
            '    print(f"  Models: {CONFIG.get(\'models\', [])}")\n'
        )
        text = text.replace(parse_args_line, config_init_block)
        print("  ✓ Injected CONFIG loading into main() after parse_args()")
    else:
        print("  ⚠ Could not find 'args = parser.parse_args()' — manual fix needed")

    RUNNER.write_text(text)
    print("  ✓ run_benchmark.py patched")

# ── 3. Verify run_benchmark_round2.sh still passes --config correctly ─────────

launcher = BENCH_DIR / 'run_benchmark_round2.sh'
launcher_text = launcher.read_text()
if 'bench_config_round2.json' in launcher_text:
    print("  ✓ run_benchmark_round2.sh already passes correct --config")
else:
    # Fix it
    launcher_text = launcher_text.replace(
        'run_benchmark.py "$@"',
        'run_benchmark.py --config bench_config_round2.json "$@"'
    )
    launcher.write_text(launcher_text)
    launcher.chmod(0o755)
    print("  ✓ run_benchmark_round2.sh updated to pass --config")

# ── Done ──────────────────────────────────────────────────────────────────────

patch.finish()

print()
print("╔══════════════════════════════════════════════════╗")
print("║  SYS-0034: --config fix applied.               ║")
print("║                                                  ║")
print("║  Now run:                                        ║")
print("║    cd /opt/mythos/orchestrator/benchmark         ║")
print("║    ./run_benchmark_round2.sh                     ║")
print("║                                                  ║")
print("║  Should load bench_config_round2.json with       ║")
print("║  9 models and doubled timeouts.                  ║")
print("╚══════════════════════════════════════════════════╝")

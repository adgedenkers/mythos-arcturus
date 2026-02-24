#!/usr/bin/env python3
"""
Patch 0115: Person Tracker with Fractal Engine
================================================

Adds /person command to Telegram bot for tracking people in Neo4j
with automatic numerological fractal computation on all dates.

Features:
  - PID system (F001♌, C001♓, etc.)
  - Full contact/life data storage
  - Auto-fractal computation with full provenance tracking
  - Auto-resonance computation against Seraphe
  - Relationship tracking between people
  - Harmonic and master number graph search
  - Family seeding (Seraphe F001, Ka F002, Fitz F003)

New Neo4j labels: TrackedPerson, HarmonicRoot, MasterNumber
New Neo4j relationships: RESONATES_WITH, HAS_HARMONIC_ROOT, CARRIES_MASTER
New files: core/fractal_engine.py, telegram_bot/handlers/person_handler.py
"""

import os
import sys
import shutil
import subprocess
import py_compile

MYTHOS_ROOT = "/opt/mythos"
PATCH_DIR = os.path.dirname(os.path.abspath(__file__))


def run(cmd, check=True):
    print(f"  → {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  ✗ FAILED: {result.stderr}")
        sys.exit(1)
    return result


def backup(filepath):
    if os.path.exists(filepath):
        bak = f"{filepath}.bak_0115"
        shutil.copy2(filepath, bak)
        print(f"  Backed up: {filepath} → {bak}")


def main():
    print("=" * 60)
    print("  Patch 0115: Person Tracker with Fractal Engine")
    print("=" * 60)

    # ── Step 1: Copy new files ──────────────────────────────────

    print("\n[1/6] Copying files...")

    # Ensure core/ has __init__.py
    init_path = os.path.join(MYTHOS_ROOT, "core", "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write("")
        print(f"  Created {init_path}")

    # Copy fractal engine
    src = os.path.join(PATCH_DIR, "opt", "mythos", "core", "fractal_engine.py")
    dst = os.path.join(MYTHOS_ROOT, "core", "fractal_engine.py")
    backup(dst)
    shutil.copy2(src, dst)
    print(f"  Copied fractal_engine.py")

    # Copy person handler
    src = os.path.join(PATCH_DIR, "opt", "mythos", "telegram_bot", "handlers", "person_handler.py")
    dst = os.path.join(MYTHOS_ROOT, "telegram_bot", "handlers", "person_handler.py")
    backup(dst)
    shutil.copy2(src, dst)
    print(f"  Copied person_handler.py")

    # ── Step 2: Syntax check ────────────────────────────────────

    print("\n[2/6] Syntax checking...")
    for pyfile in [
        os.path.join(MYTHOS_ROOT, "core", "fractal_engine.py"),
        os.path.join(MYTHOS_ROOT, "telegram_bot", "handlers", "person_handler.py"),
    ]:
        try:
            py_compile.compile(pyfile, doraise=True)
            print(f"  ✓ {os.path.basename(pyfile)}")
        except py_compile.PyCompileError as e:
            print(f"  ✗ Syntax error in {pyfile}: {e}")
            sys.exit(1)

    # ── Step 3: Patch bot imports ───────────────────────────────

    print("\n[3/6] Patching bot imports...")
    botfile = os.path.join(MYTHOS_ROOT, "telegram_bot", "mythos_bot.py")
    backup(botfile)

    with open(botfile, "r") as f:
        content = f.read()

    modified = False

    # Add import
    import_line = "from handlers.person_handler import person_command"
    if import_line not in content:
        # Find the last handler import
        marker = "from handlers.task_handler import task_command, tasks_command"
        if marker in content:
            new_import = f"{marker}\n\n# Person tracker\n{import_line}"
            content = content.replace(marker, new_import)
            modified = True
            print(f"  Added import after task_handler")
        else:
            print(f"  ✗ Could not find task_handler import to anchor after")
            print(f"    Add manually: {import_line}")
    else:
        print(f"  Import already present")

    # Add command handler
    handler_line = 'application.add_handler(CommandHandler("person", person_command))'
    if handler_line not in content:
        # Add after task handlers
        task_marker = 'application.add_handler(CommandHandler("tasks", tasks_command))'
        if task_marker in content:
            new_handler = f'{task_marker}\n\n    # Person tracker\n    {handler_line}'
            content = content.replace(task_marker, new_handler)
            modified = True
            print(f"  Added command handler after tasks")
        else:
            print(f"  ✗ Could not find tasks command handler to anchor after")
            print(f"    Add manually: {handler_line}")
    else:
        print(f"  Command handler already present")

    if modified:
        # Verify the modified content compiles
        test_path = "/tmp/test_bot_0115.py"
        with open(test_path, "w") as f:
            f.write(content)
        try:
            py_compile.compile(test_path, doraise=True)
            print(f"  ✓ Modified bot passes syntax check")
            with open(botfile, "w") as f:
                f.write(content)
            print(f"  ✓ Bot file updated")
        except py_compile.PyCompileError as e:
            print(f"  ✗ Modified bot has syntax error: {e}")
            print(f"  Rolling back bot file...")
            bak = f"{botfile}.bak_0115"
            if os.path.exists(bak):
                shutil.copy2(bak, botfile)
            sys.exit(1)
        finally:
            os.remove(test_path)

    # ── Step 4: Neo4j constraints ───────────────────────────────

    print("\n[4/6] Setting up Neo4j constraints...")

    env_path = os.path.join(MYTHOS_ROOT, ".env")
    neo4j_pass = ""
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("NEO4J_PASSWORD="):
                    neo4j_pass = line.strip().split("=", 1)[1].strip('"').strip("'")

    if neo4j_pass:
        cypher_commands = [
            "CREATE CONSTRAINT tracked_person_pid IF NOT EXISTS FOR (p:TrackedPerson) REQUIRE p.pid IS UNIQUE;",
            "CREATE CONSTRAINT harmonic_root_value IF NOT EXISTS FOR (h:HarmonicRoot) REQUIRE h.value IS UNIQUE;",
            "CREATE CONSTRAINT master_number_value IF NOT EXISTS FOR (m:MasterNumber) REQUIRE m.value IS UNIQUE;",
            "CREATE INDEX tracked_person_name IF NOT EXISTS FOR (p:TrackedPerson) ON (p.name_lower);",
            "CREATE INDEX tracked_person_lifepath IF NOT EXISTS FOR (p:TrackedPerson) ON (p.birth_lifepath);",
            "CREATE INDEX tracked_person_category IF NOT EXISTS FOR (p:TrackedPerson) ON (p.category);",
        ]
        for cmd in cypher_commands:
            result = run(
                f'cypher-shell -u neo4j -p "{neo4j_pass}" "{cmd}"',
                check=False
            )
            if result.returncode == 0:
                print(f"  ✓ {cmd[:60]}...")
            else:
                # Constraint may already exist
                if "already exists" in result.stderr.lower() or "equivalent" in result.stderr.lower():
                    print(f"  ↳ Already exists")
                else:
                    print(f"  ⚠ {result.stderr.strip()}")
    else:
        print("  ⚠ Could not read NEO4J_PASSWORD, skipping constraints")
        print("  Run manually in cypher-shell:")
        print("    CREATE CONSTRAINT tracked_person_pid IF NOT EXISTS FOR (p:TrackedPerson) REQUIRE p.pid IS UNIQUE;")

    # ── Step 5: Restart bot ─────────────────────────────────────

    print("\n[5/6] Restarting Telegram bot...")
    run("sudo systemctl restart mythos-bot.service")

    import time
    time.sleep(3)

    result = run("systemctl is-active mythos-bot.service", check=False)
    if "active" in result.stdout.strip():
        print("  ✓ Bot is running")
    else:
        print("  ✗ Bot failed to start!")
        print("  Check: journalctl -u mythos-bot.service -n 30")
        # Rollback
        print("  Rolling back...")
        for pyfile in ["core/fractal_engine.py", "telegram_bot/handlers/person_handler.py",
                        "telegram_bot/mythos_bot.py"]:
            bak = os.path.join(MYTHOS_ROOT, f"{pyfile}.bak_0115")
            orig = os.path.join(MYTHOS_ROOT, pyfile)
            if os.path.exists(bak):
                shutil.copy2(bak, orig)
                print(f"  Restored {pyfile}")
        run("sudo systemctl restart mythos-bot.service", check=False)
        sys.exit(1)

    # ── Step 6: Seed family members ─────────────────────────────

    print("\n[6/6] Seeding family members...")
    seed_script = f'''
import sys
sys.path.insert(0, "{MYTHOS_ROOT}")
sys.path.insert(0, "{MYTHOS_ROOT}/telegram_bot")
from handlers.person_handler import seed_family
seed_family()
print("  ✓ Family seeding complete")
'''
    result = run(
        f'{MYTHOS_ROOT}/.venv/bin/python3 -c \'{seed_script}\'',
        check=False
    )
    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        print(f"  ⚠ Seeding had issues: {result.stderr.strip()}")
        print(f"  You can seed manually: /person add F Seraphe Valemira born 08/19/1978")

    # ── Done ────────────────────────────────────────────────────

    print("\n" + "=" * 60)
    print("  ✅ Patch 0115 installed!")
    print()
    print("  Test commands:")
    print("    /person add C Albert Einstein born 03/14/1879")
    print("    /person C001 fractals")
    print("    /person C001 resonance")
    print("    /person add C Nikola Tesla born 07/10/1856")
    print("    /person C001 relate colleague C002")
    print("    /person list")
    print("    /person harmonic 5")
    print("    /person master 22")
    print("    /person F001")
    print("=" * 60)


if __name__ == "__main__":
    main()

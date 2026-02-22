#!/usr/bin/env python3
"""
Patch 0109: Mythos Ontology
- Neo4j OntologyTerm nodes with seed data (astrology, numerology, tarot, mythos core)
- API routes: /api/ontology/*
- Web UI: /app/ontology/
- Telegram: /define command
"""

import os
import sys
import shutil
import subprocess
import py_compile

PATCH_DIR = os.path.dirname(os.path.abspath(__file__))
MYTHOS = '/opt/mythos'


def run(cmd, check=True):
    print(f"  → {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  ✗ FAILED: {result.stderr}")
        sys.exit(1)
    return result


def copy_file(src_rel, dst):
    """Copy file from patch to destination."""
    src = os.path.join(PATCH_DIR, src_rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        shutil.copy2(dst, dst + '.bak')
        print(f"  ↳ Backed up {dst}")
    shutil.copy2(src, dst)
    print(f"  ✓ Installed {dst}")


def patch_file(filepath, old_str, new_str, description=""):
    """Replace exact string in file. Fail if not found."""
    with open(filepath, 'r') as f:
        content = f.read()
    if old_str not in content:
        print(f"  ✗ String not found in {filepath}: {description or old_str[:60]}")
        sys.exit(1)
    if new_str in content:
        print(f"  ⊘ Already patched: {description or filepath}")
        return
    content = content.replace(old_str, new_str, 1)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"  ✓ Patched {filepath}: {description}")


def main():
    print("═══ Patch 0109: Mythos Ontology ═══\n")

    # 1. Copy files
    print("1. Installing files...")
    copy_file('opt/mythos/core/ontology_seed.py', f'{MYTHOS}/core/ontology_seed.py')
    copy_file('opt/mythos/api/routes/ontology.py', f'{MYTHOS}/api/routes/ontology.py')
    copy_file('opt/mythos/web/templates/ontology.html', f'{MYTHOS}/web/templates/ontology.html')
    copy_file('opt/mythos/telegram_bot/handlers/ontology_handler.py', f'{MYTHOS}/telegram_bot/handlers/ontology_handler.py')

    # 2. Syntax check all Python files
    print("\n2. Syntax checking...")
    for pyfile in [
        f'{MYTHOS}/core/ontology_seed.py',
        f'{MYTHOS}/api/routes/ontology.py',
        f'{MYTHOS}/telegram_bot/handlers/ontology_handler.py',
    ]:
        py_compile.compile(pyfile, doraise=True)
        print(f"  ✓ {pyfile}")

    # 3. Register ontology API route in main.py
    print("\n3. Registering API route...")
    main_py = f'{MYTHOS}/api/main.py'

    # Add import
    patch_file(
        main_py,
        "from api.routes.web import router as web_router",
        "from api.routes.web import router as web_router\nfrom api.routes.ontology import router as ontology_router",
        "Add ontology import"
    )

    # Add router include (after web_router)
    patch_file(
        main_py,
        "app.include_router(web_router)",
        "app.include_router(web_router)\napp.include_router(ontology_router)",
        "Include ontology router"
    )

    # 4. Add web route for /app/ontology/
    print("\n4. Adding web route...")
    web_py = f'{MYTHOS}/api/routes/web.py'

    patch_file(
        web_py,
        """# Registry
@router.get("/registry/", response_class=HTMLResponse)
@router.get("/registry", response_class=HTMLResponse)
async def registry_page(request: Request):
    return serve('registry.html')""",
        """# Ontology
@router.get("/ontology/", response_class=HTMLResponse)
@router.get("/ontology", response_class=HTMLResponse)
async def ontology_page(request: Request):
    return serve('ontology.html')


# Registry
@router.get("/registry/", response_class=HTMLResponse)
@router.get("/registry", response_class=HTMLResponse)
async def registry_page(request: Request):
    return serve('registry.html')""",
        "Add ontology web route"
    )

    # 5. Wire /define command into Telegram bot
    print("\n5. Wiring Telegram /define command...")
    bot_py = f'{MYTHOS}/telegram_bot/mythos_bot.py'

    # Read the bot file to find the right injection point
    with open(bot_py, 'r') as f:
        bot_content = f.read()

    # Add import if not present
    if 'ontology_handler' not in bot_content:
        # Find import section — add after last handler import
        if 'from handlers.' in bot_content:
            # Find the last "from handlers." import line
            lines = bot_content.split('\n')
            last_handler_import_idx = -1
            for i, line in enumerate(lines):
                if line.strip().startswith('from handlers.') or line.strip().startswith('from telegram_bot.handlers.'):
                    last_handler_import_idx = i

            if last_handler_import_idx >= 0:
                import_line = lines[last_handler_import_idx]
                new_import = import_line.rsplit('from ', 1)
                # Determine import style
                if 'from handlers.' in import_line:
                    ontology_import = "from handlers.ontology_handler import handle_define"
                else:
                    ontology_import = "from telegram_bot.handlers.ontology_handler import handle_define"

                lines.insert(last_handler_import_idx + 1, ontology_import)
                bot_content = '\n'.join(lines)
                with open(bot_py, 'w') as f:
                    f.write(bot_content)
                print(f"  ✓ Added ontology import to bot")
            else:
                print("  ⚠ Could not find handler imports in bot — add manually:")
                print("    from handlers.ontology_handler import handle_define")
        else:
            print("  ⚠ No handler imports found — add manually")

    # Add command handler registration
    # Look for pattern of command handler registration
    with open(bot_py, 'r') as f:
        bot_content = f.read()

    if 'define' not in bot_content:
        # Try to find where commands are registered — look for CommandHandler or app.add_handler
        if 'CommandHandler' in bot_content:
            # Find a good injection point near other CommandHandler lines
            lines = bot_content.split('\n')
            last_cmd_idx = -1
            for i, line in enumerate(lines):
                if 'CommandHandler' in line and 'add_handler' in line:
                    last_cmd_idx = i

            if last_cmd_idx >= 0:
                indent = '    '  # typical indent
                existing_line = lines[last_cmd_idx]
                # Determine indent from existing line
                indent = existing_line[:len(existing_line) - len(existing_line.lstrip())]

                define_handler = f"""
{indent}# Ontology
{indent}async def define_cmd(update, context):
{indent}    text = ' '.join(context.args) if context.args else ''
{indent}    result = handle_define(text)
{indent}    await update.message.reply_text(result)
{indent}app.add_handler(CommandHandler('define', define_cmd))"""

                lines.insert(last_cmd_idx + 1, define_handler)
                bot_content = '\n'.join(lines)
                with open(bot_py, 'w') as f:
                    f.write(bot_content)
                print("  ✓ Added /define command handler to bot")
            else:
                print("  ⚠ Could not find CommandHandler pattern — add /define manually")
        else:
            print("  ⚠ Bot uses non-standard command registration — add /define manually")
    else:
        print("  ⊘ /define already registered in bot")

    # 6. Add Ontology nav link to home.html
    print("\n6. Updating navigation...")
    home_html = f'{MYTHOS}/web/templates/home.html'

    # Add nav link
    patch_file(
        home_html,
        '<a href="/app/system/">System</a>',
        '<a href="/app/ontology/">Ontology</a>\n    <a href="/app/system/">System</a>',
        "Add Ontology to home nav"
    )

    # Add nav link to dashboard.html too if topbar nav exists
    dash_html = f'{MYTHOS}/web/templates/dashboard.html'
    if os.path.exists(dash_html):
        with open(dash_html, 'r') as f:
            dash_content = f.read()
        if '/app/ontology/' not in dash_content and '<a href="/app/system/"' in dash_content:
            dash_content = dash_content.replace(
                '<a href="/app/system/"',
                '<a href="/app/ontology/">Ontology</a>\n    <a href="/app/system/"',
                1
            )
            with open(dash_html, 'w') as f:
                f.write(dash_content)
            print("  ✓ Added Ontology to dashboard nav")

    # Syntax check modified files
    print("\n7. Final syntax checks...")
    py_compile.compile(main_py, doraise=True)
    py_compile.compile(web_py, doraise=True)
    print("  ✓ All Python files pass syntax check")

    # 8. Seed Neo4j
    print("\n8. Seeding ontology terms in Neo4j...")
    seed_result = run(
        f'{MYTHOS}/.venv/bin/python3 {MYTHOS}/core/ontology_seed.py',
        check=False
    )
    if seed_result.returncode == 0:
        print(seed_result.stdout)
    else:
        print(f"  ⚠ Seed script had issues: {seed_result.stderr}")
        print("  Run manually: /opt/mythos/.venv/bin/python3 /opt/mythos/core/ontology_seed.py")

    # 9. Restart services
    print("\n9. Restarting services...")
    run('sudo systemctl restart mythos-api.service', check=False)
    run('sudo systemctl restart mythos-bot.service', check=False)

    # Verify
    import time
    time.sleep(3)
    api_check = run('systemctl is-active mythos-api.service', check=False)
    bot_check = run('systemctl is-active mythos-bot.service', check=False)

    api_ok = 'active' in api_check.stdout
    bot_ok = 'active' in bot_check.stdout

    print(f"\n  API: {'✓ active' if api_ok else '✗ ' + api_check.stdout.strip()}")
    print(f"  Bot: {'✓ active' if bot_ok else '✗ ' + bot_check.stdout.strip()}")

    if not api_ok:
        print("\n  ⚠ API failed to start. Check: journalctl -u mythos-api.service -n 30 --no-pager")
        # Rollback modified files
        for f in [main_py, web_py]:
            bak = f + '.bak'
            if os.path.exists(bak):
                shutil.copy2(bak, f)
                print(f"  ↶ Rolled back {f}")
        run('sudo systemctl restart mythos-api.service', check=False)
        sys.exit(1)

    print("\n═══ Patch 0109 Complete ═══")
    print("  • Ontology API: /api/ontology/terms")
    print("  • Web UI: /app/ontology/")
    print("  • Telegram: /define <term>")
    print(f"  • Terms seeded in Neo4j")


if __name__ == '__main__':
    main()

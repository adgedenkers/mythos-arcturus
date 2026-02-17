#!/usr/bin/env python3
"""
Patch 0087 install - Finance import notification fix
Only patches the _notify_finance_import condition in mythos_patch_monitor.py
"""
import re
from pathlib import Path

MONITOR = Path("/opt/mythos/mythos_patch_monitor.py")

old = '''                # Send Telegram notification
                if TELEGRAM_NOTIFY_FINANCE and imported > 0:
                    self._notify_finance_import(bank, imported, skipped)'''

new = '''                # Send Telegram notification (always — even all-skipped confirms it ran)
                if TELEGRAM_NOTIFY_FINANCE:
                    self._notify_finance_import(bank, imported, skipped)'''

old_method = '''    def _notify_finance_import(self, bank: str, imported: int, skipped: int):
        """Send success notification via Telegram"""
        try:
            msg = f"✅ *Finance Auto-Import*\\n\\n"
            msg += f"Bank: {bank.upper()}\\n"
            msg += f"Imported: {imported} new transactions\\n"
            if skipped > 0:
                msg += f"Skipped: {skipped} (duplicates)\\n"
            send_telegram_notification(msg)
        except Exception as e:
            logger.debug(f"Could not send import notification: {e}")'''

new_method = '''    def _notify_finance_import(self, bank: str, imported: int, skipped: int):
        """Send import result notification via Telegram"""
        try:
            if imported > 0:
                msg = f"✅ *Finance Import Complete*\\n\\n"
                msg += f"Bank: {bank.upper()}\\n"
                msg += f"New: {imported} transactions imported\\n"
                if skipped > 0:
                    msg += f"Skipped: {skipped} (already in DB)\\n"
            else:
                msg = f"ℹ️ *Finance Import — Up to Date*\\n\\n"
                msg += f"Bank: {bank.upper()}\\n"
                msg += f"All {skipped} transactions already in DB\\n"
                msg += f"No new data\\n"
            send_telegram_notification(msg)
        except Exception as e:
            logger.debug(f"Could not send import notification: {e}")'''

content = MONITOR.read_text()

if old not in content:
    print("ERROR: Could not find notification condition to patch")
    print("Searched for:")
    print(repr(old))
    exit(1)

if old_method not in content:
    print("ERROR: Could not find _notify_finance_import method to patch")
    exit(1)

content = content.replace(old, new)
content = content.replace(old_method, new_method)
MONITOR.write_text(content)
print("✓ Patched mythos_patch_monitor.py")

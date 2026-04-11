#!/usr/bin/env python3
"""
SYS-0057_rode_autotransfer_fix

Completes the SYS-0056 install. SYS-0056 successfully patched
rode_transfer.py with the --yes flag, but failed mid-deploy because
PatchBase wrote /opt/mythos/bin/rode-autotransfer as root and the
subsequent os.chmod (running as adge) hit EPERM.

This patch:
1. Removes the stale root-owned /opt/mythos/bin/rode-autotransfer (sudo)
2. Deploys the wrapper, udev rule, and systemd unit via sudo
3. Reloads udev and systemd
4. Ensures /opt/mythos/logs/rode_autotransfer.log exists

Does NOT touch rode_transfer.py — it was already patched in SYS-0056.
"""
import sys
import os
import subprocess
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

PATCH_DIR = Path(__file__).parent.resolve()


def run_sudo(cmd: list, description: str):
    print(f"  → {description}")
    full = ['sudo'] + cmd
    result = subprocess.run(full, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ FAILED: {' '.join(full)}")
        print(f"    stdout: {result.stdout}")
        print(f"    stderr: {result.stderr}")
        sys.exit(1)
    if result.stdout.strip():
        print(f"    {result.stdout.strip()}")


def main():
    patch = PatchBase(
        stream='SYS',
        number=57,
        description='rode_autotransfer_fix',
        patch_type='PATCH',
    )
    patch.begin()

    # ── 1. Remove stale rode-autotransfer if present (root-owned from SYS-0056) ──
    stale = Path('/opt/mythos/bin/rode-autotransfer')
    if stale.exists():
        st = stale.stat()
        # Only remove if not owned by adge (uid 1000 typically — but check by trying)
        try:
            # If we can unlink it, do so. Otherwise sudo.
            stale.unlink()
            print(f"  → Removed stale {stale} (was adge-owned)")
        except PermissionError:
            run_sudo(['rm', '-f', str(stale)], f'Remove stale root-owned {stale}')

    # ── 2. Deploy rode-autotransfer via sudo install (sets perms in one shot) ──
    src = PATCH_DIR / 'opt/mythos/bin/rode-autotransfer'
    run_sudo(
        ['install', '-o', 'adge', '-g', 'adge', '-m', '0755',
         str(src), '/opt/mythos/bin/rode-autotransfer'],
        'Install rode-autotransfer (adge:adge 0755)'
    )

    # ── 3. Ensure logs directory and log file ────────────────────────────────
    logs_dir = Path('/opt/mythos/logs')
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / 'rode_autotransfer.log'
    if not log_file.exists():
        log_file.touch()
    try:
        os.chmod(log_file, 0o664)
    except PermissionError:
        run_sudo(['chown', 'adge:adge', str(log_file)], 'Reclaim log file ownership')
        run_sudo(['chmod', '664', str(log_file)], 'Set log file perms')

    # ── 4. Install udev rule ─────────────────────────────────────────────────
    udev_src = PATCH_DIR / 'etc/udev/rules.d/99-rode-autotransfer.rules'
    run_sudo(
        ['install', '-o', 'root', '-g', 'root', '-m', '0644',
         str(udev_src), '/etc/udev/rules.d/99-rode-autotransfer.rules'],
        'Install udev rule'
    )

    # ── 5. Install systemd unit ──────────────────────────────────────────────
    unit_src = PATCH_DIR / 'etc/systemd/system/rode-autotransfer.service'
    run_sudo(
        ['install', '-o', 'root', '-g', 'root', '-m', '0644',
         str(unit_src), '/etc/systemd/system/rode-autotransfer.service'],
        'Install systemd unit'
    )

    # ── 6. Reload udev and systemd ───────────────────────────────────────────
    run_sudo(['udevadm', 'control', '--reload-rules'], 'Reload udev rules')
    run_sudo(['udevadm', 'trigger'], 'Trigger udev')
    run_sudo(['systemctl', 'daemon-reload'], 'Reload systemd daemon')

    # ── 7. Verification ──────────────────────────────────────────────────────
    print()
    print("  Verification:")
    for path in [
        '/opt/mythos/bin/rode-autotransfer',
        '/etc/udev/rules.d/99-rode-autotransfer.rules',
        '/etc/systemd/system/rode-autotransfer.service',
    ]:
        if Path(path).exists():
            print(f"    ✓ {path}")
        else:
            print(f"    ✗ MISSING: {path}")
            sys.exit(1)

    print()
    print("  ✓ rode-autotransfer fully installed")
    print("  ✓ Test manual run:  sudo systemctl start rode-autotransfer.service")
    print("  ✓ Watch log:        tail -f /opt/mythos/logs/rode_autotransfer.log")
    print("  ✓ Real test:        unplug TX, replug, watch log within 20s")
    print()

    patch.finish()


if __name__ == '__main__':
    main()

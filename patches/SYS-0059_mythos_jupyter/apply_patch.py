#!/usr/bin/env python3
"""
SYS-0059: mythos-jupyter service + demo prep script

v2 — fully idempotent. Detects and skips anything already in place from a
prior install attempt. Does not touch sudo'd /etc/ files in rollback tracking
(they are owned by root and cannot be removed by PatchBase as adge).

Deploys:
  - /opt/mythos/.venv-jupyter/         (dedicated venv)
  - /opt/mythos/bin/mythos-jupyter-launcher
  - /opt/mythos/bin/jupyter-token
  - /opt/mythos/bin/jupyter-rotate-token
  - /opt/mythos/demo/prep_demo_graphs.sh
  - /opt/mythos/demo/repos/              (empty, ready for strapi clone)
  - /opt/mythos/notebooks/README.md
  - /opt/mythos/.jupyter/                (jupyter config/data/runtime dirs)
  - /opt/mythos/.jupyter_token           (generated on first install)
  - /etc/systemd/system/mythos-jupyter.service  (via sudo, not tracked for rollback)

Side effects (not rollback-tracked — must be reversed manually if needed):
  - Appends `jupyter.denkers.co` ingress rule to /etc/cloudflared/config.yml
  - Adds DNS route `jupyter.denkers.co` to the `mythos` tunnel

Does NOT:
  - Clone strapi (run prep_demo_graphs.sh manually for that)
  - Touch demo Neo4j containers
  - Deploy the autodoc2 demo notebook (that's SYS-0061)
"""

import os
import sys
import json
import shutil
import secrets
import subprocess
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

# ─── Configuration ───────────────────────────────────────────────────────────

JUPYTER_VENV = Path("/opt/mythos/.venv-jupyter")
JUPYTER_CONFIG_DIR = Path("/opt/mythos/.jupyter")
TOKEN_FILE = Path("/opt/mythos/.jupyter_token")
NOTEBOOKS_DIR = Path("/opt/mythos/notebooks")
DEMO_DIR = Path("/opt/mythos/demo")
DEMO_REPOS_DIR = DEMO_DIR / "repos"

SYSTEMD_UNIT_SRC = "etc/systemd/system/mythos-jupyter.service"
SYSTEMD_UNIT_DST = "/etc/systemd/system/mythos-jupyter.service"

CLOUDFLARED_CONFIG = Path("/etc/cloudflared/config.yml")
CLOUDFLARED_TUNNEL_NAME = "mythos"
JUPYTER_HOSTNAME = "jupyter.denkers.co"
JUPYTER_LOCAL_URL = "http://127.0.0.1:8899"

# Pip packages for the Jupyter venv. Only installed if missing.
JUPYTER_PACKAGES = [
    "jupyterlab>=4.0",
    "notebook>=7.0",
    "ipykernel>=6.0",
    "pandas>=2.0",
    "matplotlib>=3.7",
    "networkx>=3.0",
    "neo4j>=5.0",
    "requests>=2.31",
]


# ─── Helpers ─────────────────────────────────────────────────────────────────

def run(cmd, check=True, capture=True, input_text=None, env=None):
    """Run a subprocess, return the CompletedProcess."""
    return subprocess.run(
        cmd,
        check=check,
        capture_output=capture,
        text=True,
        input=input_text,
        env=env,
    )


def log(patch, msg):
    patch.logger.log(f"  → {msg}")


def log_skip(patch, msg):
    patch.logger.log(f"  ⊙ {msg}")


def log_ok(patch, msg):
    patch.logger.log(f"  ✓ {msg}")


def file_content_equal(src_path: Path, dst_path: str) -> bool:
    """Check if two files have identical content."""
    try:
        src_bytes = src_path.read_bytes()
        # Read dst as current user first; if permission denied, fall back to sudo cat
        try:
            dst_bytes = Path(dst_path).read_bytes()
        except PermissionError:
            result = run(["sudo", "cat", dst_path], check=False)
            if result.returncode != 0:
                return False
            dst_bytes = result.stdout.encode()
        return src_bytes == dst_bytes
    except Exception:
        return False


# ─── Step: Ensure directories exist ──────────────────────────────────────────

def ensure_directories(patch):
    """Create notebooks/, demo/, demo/repos/, .jupyter/ subdirs if missing."""
    dirs = [
        NOTEBOOKS_DIR,
        DEMO_DIR,
        DEMO_REPOS_DIR,
        JUPYTER_CONFIG_DIR,
        JUPYTER_CONFIG_DIR / "data",
        JUPYTER_CONFIG_DIR / "runtime",
    ]
    for d in dirs:
        if patch.dry_run:
            if not d.exists():
                log(patch, f"[validate] would create {d}")
            continue
        try:
            if d.exists():
                log_skip(patch, f"already exists: {d}")
            else:
                d.mkdir(parents=True, exist_ok=True)
                log_ok(patch, f"created {d}")
        except Exception as e:
            patch.errors.append(f"mkdir {d}: {e}")


# ─── Step: Provision Jupyter venv (skip if already usable) ───────────────────

def ensure_jupyter_venv(patch):
    """
    Create /opt/mythos/.venv-jupyter/ if missing, install packages if absent.
    Skips everything if the venv already has jupyterlab importable.
    """
    venv_py = JUPYTER_VENV / "bin" / "python3"

    # Fast path: if venv exists AND jupyterlab imports cleanly, skip entirely
    if venv_py.exists():
        try:
            result = run(
                [str(venv_py), "-c",
                 "import jupyterlab, pandas, matplotlib, networkx, neo4j, requests; "
                 "print('ok')"],
                check=False,
            )
            if result.returncode == 0 and "ok" in result.stdout:
                log_skip(patch, f"venv already provisioned at {JUPYTER_VENV} (jupyterlab importable)")
                patch.validations.append("jupyter venv already usable")
                return
        except Exception:
            pass  # fall through to provision

    if patch.dry_run:
        log(patch, f"[validate] would provision venv at {JUPYTER_VENV}")
        return

    # Create venv if missing
    if not JUPYTER_VENV.exists():
        log(patch, f"creating venv at {JUPYTER_VENV}")
        try:
            run(["/usr/bin/python3", "-m", "venv", str(JUPYTER_VENV)])
            log_ok(patch, "venv created")
        except subprocess.CalledProcessError as e:
            patch.errors.append(f"venv creation failed: {e.stderr}")
            return

    venv_pip = JUPYTER_VENV / "bin" / "pip"
    if not venv_pip.exists():
        patch.errors.append(f"venv pip not found at {venv_pip}")
        return

    log(patch, "upgrading pip in venv")
    try:
        run([str(venv_pip), "install", "--quiet", "--upgrade", "pip"])
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"pip upgrade failed: {e.stderr}")
        return

    log(patch, f"installing {len(JUPYTER_PACKAGES)} packages (this may take 60-90s)")
    try:
        run([str(venv_pip), "install", "--quiet"] + JUPYTER_PACKAGES)
        log_ok(patch, "all packages installed")
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"pip install failed: {e.stderr}")
        return

    # Verify
    try:
        run([str(venv_py), "-c",
             "import jupyterlab, pandas, matplotlib, networkx, neo4j, requests; print('ok')"])
        log_ok(patch, "venv import sanity check passed")
        patch.validations.append("jupyter venv usable")
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"venv sanity check failed: {e.stderr}")


# ─── Step: Generate initial Jupyter token if missing ─────────────────────────

def ensure_jupyter_token(patch):
    """Generate /opt/mythos/.jupyter_token if it doesn't exist. Idempotent."""
    if patch.dry_run:
        if TOKEN_FILE.exists():
            log_skip(patch, f"token file {TOKEN_FILE} already present")
        else:
            log(patch, f"[validate] would generate new token")
        return

    if TOKEN_FILE.exists():
        log_skip(patch, f"token file exists at {TOKEN_FILE} — leaving alone")
        return

    try:
        token = secrets.token_urlsafe(48)
        # Atomic write: tmp file + rename. Use explicit concat; .with_suffix
        # would replace the (nonexistent) extension and mangle the name.
        tmp = Path(str(TOKEN_FILE) + ".tmp")
        tmp.write_text(token)
        os.chmod(tmp, 0o600)
        tmp.rename(TOKEN_FILE)
        log_ok(patch, f"generated new token at {TOKEN_FILE} (mode 0600)")
        patch.validations.append("jupyter token generated")
    except Exception as e:
        patch.errors.append(f"token generation: {e}")


# ─── Step: Set executable bits on deployed scripts ───────────────────────────

EXECUTABLE_SCRIPTS = [
    "/opt/mythos/bin/mythos-jupyter-launcher",
    "/opt/mythos/bin/jupyter-token",
    "/opt/mythos/bin/jupyter-rotate-token",
    "/opt/mythos/demo/prep_demo_graphs.sh",
]


def ensure_executable(patch):
    if patch.dry_run:
        log(patch, f"[validate] would chmod +x {len(EXECUTABLE_SCRIPTS)} scripts")
        return
    for path in EXECUTABLE_SCRIPTS:
        p = Path(path)
        if not p.exists():
            patch.errors.append(f"chmod +x: {path} does not exist")
            continue
        try:
            current = p.stat().st_mode
            p.chmod(current | 0o111)
            log_ok(patch, f"chmod +x {path}")
        except Exception as e:
            patch.errors.append(f"chmod {path}: {e}")


# ─── Step: Deploy systemd unit (NOT tracked in files_deployed) ───────────────

def deploy_systemd_unit(patch):
    """
    Deploy the systemd unit to /etc/systemd/system/ via sudo.

    CRITICAL: This file is NOT added to patch.files_deployed because PatchBase's
    rollback attempts to unlink tracked files as the patch user (adge), which
    cannot remove root-owned /etc/ files. If this install fails downstream and
    PatchBase rolls back, the unit file stays on disk — that's acceptable
    because this function is idempotent: on re-install, it detects and skips.

    We only sudo-deploy the unit if:
      - It doesn't exist, OR
      - The existing content differs from what we're shipping
    Otherwise we skip entirely.
    """
    src = patch.patch_dir / SYSTEMD_UNIT_SRC
    if not src.exists():
        patch.errors.append(f"systemd unit source missing: {src}")
        return

    # Idempotency check
    if Path(SYSTEMD_UNIT_DST).exists() and file_content_equal(src, SYSTEMD_UNIT_DST):
        log_skip(patch, f"systemd unit already matches at {SYSTEMD_UNIT_DST}")
        # Still do daemon-reload + enable in case previous install was incomplete
        if not patch.dry_run:
            try:
                run(["sudo", "systemctl", "daemon-reload"])
                log_ok(patch, "systemctl daemon-reload (no-op)")
            except subprocess.CalledProcessError as e:
                patch.errors.append(f"daemon-reload: {e.stderr}")
                return
            # Ensure it's enabled
            enabled = run(
                ["systemctl", "is-enabled", "mythos-jupyter.service"],
                check=False,
            )
            if "enabled" not in (enabled.stdout or ""):
                try:
                    run(["sudo", "systemctl", "enable", "mythos-jupyter.service"])
                    log_ok(patch, "enabled mythos-jupyter.service")
                except subprocess.CalledProcessError as e:
                    patch.errors.append(f"systemctl enable: {e.stderr}")
                    return
            else:
                log_skip(patch, "mythos-jupyter.service already enabled")
        patch.validations.append("systemd unit already in place")
        return

    if patch.dry_run:
        log(patch, f"[validate] would sudo cp {src} → {SYSTEMD_UNIT_DST}")
        return

    # Actually deploy
    try:
        run(["sudo", "cp", str(src), SYSTEMD_UNIT_DST])
        run(["sudo", "chmod", "0644", SYSTEMD_UNIT_DST])
        run(["sudo", "chown", "root:root", SYSTEMD_UNIT_DST])
        log_ok(patch, f"deployed {SYSTEMD_UNIT_DST}")
        # NOTE: deliberately NOT appending to patch.files_deployed — rollback
        # cannot remove this file as adge, and it's idempotent on re-install.
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"deploy systemd unit: {e.stderr}")
        return

    try:
        run(["sudo", "systemctl", "daemon-reload"])
        log_ok(patch, "systemctl daemon-reload")
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"daemon-reload: {e.stderr}")
        return

    try:
        run(["sudo", "systemctl", "enable", "mythos-jupyter.service"])
        log_ok(patch, "enabled mythos-jupyter.service")
    except subprocess.CalledProcessError as e:
        if "already" in (e.stderr or "").lower():
            log_skip(patch, "mythos-jupyter.service already enabled")
        else:
            patch.errors.append(f"systemctl enable: {e.stderr}")


# ─── Step: Append Jupyter ingress rule to cloudflared config ─────────────────

def ensure_cloudflared_ingress(patch):
    """
    Read /etc/cloudflared/config.yml, check if jupyter.denkers.co is already
    routed, and if not, insert a new ingress rule BEFORE the catch-all 404.
    Validates the result with `cloudflared tunnel ingress validate` before writing.
    Backs up the existing config to /tmp so manual rollback is trivial.

    NOT tracked in files_deployed — this file is root-owned and cannot be
    reverted by PatchBase's rollback. Rollback is manual:
        sudo cp /tmp/cloudflared_config.yml.SYS-0059.bak /etc/cloudflared/config.yml
    """
    if not CLOUDFLARED_CONFIG.exists():
        patch.errors.append(f"cloudflared config not found at {CLOUDFLARED_CONFIG}")
        return

    try:
        current = CLOUDFLARED_CONFIG.read_text()
    except Exception as e:
        patch.errors.append(f"cannot read cloudflared config: {e}")
        return

    if JUPYTER_HOSTNAME in current:
        log_skip(patch, f"{JUPYTER_HOSTNAME} already in cloudflared config")
        patch.validations.append(f"cloudflared ingress {JUPYTER_HOSTNAME} — already present")
        return

    if patch.dry_run:
        log(patch, f"[validate] would append {JUPYTER_HOSTNAME} → {JUPYTER_LOCAL_URL}")
        return

    # Find the catch-all line and insert our rule before it.
    lines = current.splitlines(keepends=True)
    new_lines = []
    inserted = False

    new_rule_lines = [
        f"  - hostname: {JUPYTER_HOSTNAME}\n",
        f"    service: {JUPYTER_LOCAL_URL}\n",
    ]

    for line in lines:
        stripped = line.strip()
        if not inserted and stripped.startswith("- service: http_status"):
            new_lines.extend(new_rule_lines)
            inserted = True
        new_lines.append(line)

    if not inserted:
        patch.errors.append("could not find catch-all rule in cloudflared config — refusing to append")
        return

    new_config = "".join(new_lines)

    tmp_path = "/tmp/mythos_cloudflared_config.yml.new"
    backup_path = "/tmp/cloudflared_config.yml.SYS-0059.bak"
    try:
        with open(tmp_path, "w") as f:
            f.write(new_config)

        # Validate with cloudflared itself. Correct global-flag ordering:
        # `cloudflared --config <path> tunnel ingress validate`
        result = run(
            ["cloudflared", "--config", tmp_path, "tunnel", "ingress", "validate"],
            check=False,
        )
        if result.returncode != 0:
            patch.errors.append(
                f"cloudflared ingress validation failed:\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
            return

        log_ok(patch, "cloudflared config validates cleanly")

        # Back up before overwriting
        shutil.copy2(str(CLOUDFLARED_CONFIG), backup_path)
        log_ok(patch, f"backed up existing config to {backup_path}")

        # Move new config into place with sudo
        run(["sudo", "cp", tmp_path, str(CLOUDFLARED_CONFIG)])
        run(["sudo", "chmod", "0644", str(CLOUDFLARED_CONFIG)])
        run(["sudo", "chown", "root:root", str(CLOUDFLARED_CONFIG)])
        log_ok(patch, f"appended {JUPYTER_HOSTNAME} ingress rule")
        log(patch, f"rollback: sudo cp {backup_path} {CLOUDFLARED_CONFIG}")
        # NOT added to patch.files_deployed — root-owned, PatchBase can't revert.
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"cloudflared config write: {e.stderr}")
    except Exception as e:
        patch.errors.append(f"cloudflared config write: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ─── Step: Add DNS route (as adge, not sudo) ─────────────────────────────────

def ensure_dns_route(patch):
    """
    Add DNS route jupyter.denkers.co → mythos tunnel.

    CRITICAL: Run as adge, NOT sudo. `cloudflared tunnel route dns` needs the
    origin cert at ~/.cloudflared/cert.pem, which lives in adge's home. sudo'd
    invocations look in /root/.cloudflared/ and fail.

    Idempotency: check DNS resolution first via `dig`. If the hostname already
    resolves, skip the route add.
    """
    if patch.dry_run:
        log(patch, f"[validate] would ensure DNS route {JUPYTER_HOSTNAME}")
        return

    # First check if it's already resolvable
    dig_result = run(["dig", "+short", JUPYTER_HOSTNAME], check=False)
    resolved = (dig_result.stdout or "").strip()
    if resolved:
        log_skip(patch, f"{JUPYTER_HOSTNAME} already resolves ({resolved.split(chr(10))[0]})")
        patch.validations.append(f"DNS route {JUPYTER_HOSTNAME} already exists")
        return

    # Not resolvable — add the route. Run as adge (no sudo), explicit HOME so
    # cloudflared finds cert.pem in /home/adge/.cloudflared/.
    try:
        env = os.environ.copy()
        env["HOME"] = str(Path.home())
        result = run(
            ["cloudflared", "tunnel", "route", "dns",
             CLOUDFLARED_TUNNEL_NAME, JUPYTER_HOSTNAME],
            check=False,
            env=env,
        )
        combined = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0:
            log_ok(patch, f"DNS route added: {JUPYTER_HOSTNAME}")
            patch.validations.append(f"DNS route {JUPYTER_HOSTNAME} created")
        elif "already exists" in combined.lower() or "record with that name" in combined.lower():
            log_skip(patch, f"DNS route {JUPYTER_HOSTNAME} already exists on Cloudflare side")
            patch.validations.append(f"DNS route {JUPYTER_HOSTNAME} already exists")
        else:
            patch.errors.append(f"DNS route add failed: {combined.strip()}")
    except Exception as e:
        patch.errors.append(f"DNS route add: {e}")


# ─── Step: Verify cloudflared is active after any config change ──────────────

def verify_cloudflared_active(patch):
    """Poll cloudflared.service is-active. Used after a config edit + restart."""
    if patch.dry_run:
        return

    import time
    log(patch, "waiting for cloudflared.service to become active (up to 20s)")

    for attempt in range(20):
        time.sleep(1)
        result = run(
            ["systemctl", "is-active", "cloudflared.service"],
            check=False,
        )
        state = (result.stdout or "").strip()
        if state == "active":
            log_ok(patch, f"cloudflared.service is active (took {attempt + 1}s)")
            patch.validations.append("cloudflared.service active")
            return
        if state == "failed":
            break

    journal = run(
        ["journalctl", "-u", "cloudflared.service", "-n", "30", "--no-pager"],
        check=False,
    )
    patch.errors.append(
        f"cloudflared.service did not reach active state.\n"
        f"Rollback: sudo cp /tmp/cloudflared_config.yml.SYS-0059.bak {CLOUDFLARED_CONFIG}\n"
        f"         sudo systemctl restart cloudflared.service\n"
        f"Last 30 lines of journal:\n{journal.stdout}"
    )


# ─── Step: Start (or restart) mythos-jupyter and verify ──────────────────────

def start_jupyter_and_verify(patch):
    """
    Start mythos-jupyter.service if it's inactive, or restart if it's running.
    Poll is-active for up to 30 seconds and fail with journal output if it
    never reaches active state.
    """
    if patch.dry_run:
        log(patch, "[validate] would start/restart mythos-jupyter.service and poll is-active")
        return

    # Check current state
    state_result = run(
        ["systemctl", "is-active", "mythos-jupyter.service"],
        check=False,
    )
    current_state = (state_result.stdout or "").strip()

    if current_state == "active":
        log(patch, "mythos-jupyter.service already active — restarting to pick up any changes")
        action = "restart"
    else:
        log(patch, f"mythos-jupyter.service is {current_state} — starting")
        action = "start"

    try:
        run(["sudo", "systemctl", action, "--no-block", "mythos-jupyter.service"])
        log_ok(patch, f"{action} mythos-jupyter.service (async)")
    except subprocess.CalledProcessError as e:
        patch.errors.append(f"{action} mythos-jupyter: {e.stderr}")
        return

    import time
    log(patch, "waiting for mythos-jupyter.service to become active (up to 30s)")

    for attempt in range(30):
        time.sleep(1)
        result = run(
            ["systemctl", "is-active", "mythos-jupyter.service"],
            check=False,
        )
        state = (result.stdout or "").strip()
        if state == "active":
            log_ok(patch, f"mythos-jupyter.service is active (took {attempt + 1}s)")
            patch.validations.append("mythos-jupyter.service active")
            # Track the restart in PatchBase's services list for the PATCH_HISTORY entry
            if "mythos-jupyter.service" not in patch.services_restarted:
                patch.services_restarted.append("mythos-jupyter.service")
            return
        if state == "failed":
            break

    journal = run(
        ["journalctl", "-u", "mythos-jupyter.service", "-n", "30", "--no-pager"],
        check=False,
    )
    patch.errors.append(
        f"mythos-jupyter.service did not reach active state.\n"
        f"Last 30 lines of journal:\n{journal.stdout}"
    )


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    patch = PatchBase(
        stream='SYS',
        number=59,
        description='mythos-jupyter service + demo prep script',
        patch_type='MINOR',
    )
    patch.begin()

    # ── 1. Ensure directories ────────────────────────────────────────────
    patch.logger.log("\n[1/8] Ensuring directories")
    ensure_directories(patch)
    if patch.errors: patch.finish(); return 1

    # ── 2. Provision Jupyter venv (skip if already usable) ───────────────
    patch.logger.log("\n[2/8] Provisioning Jupyter venv")
    ensure_jupyter_venv(patch)
    if patch.errors: patch.finish(); return 1

    # ── 3. Deploy /opt/mythos/ files via PatchBase ───────────────────────
    patch.logger.log("\n[3/8] Deploying files")
    patch.deploy_file(
        'opt/mythos/bin/mythos-jupyter-launcher',
        '/opt/mythos/bin/mythos-jupyter-launcher',
    )
    patch.deploy_file(
        'opt/mythos/bin/jupyter-token',
        '/opt/mythos/bin/jupyter-token',
    )
    patch.deploy_file(
        'opt/mythos/bin/jupyter-rotate-token',
        '/opt/mythos/bin/jupyter-rotate-token',
    )
    patch.deploy_file(
        'opt/mythos/demo/prep_demo_graphs.sh',
        '/opt/mythos/demo/prep_demo_graphs.sh',
    )
    patch.deploy_file(
        'opt/mythos/notebooks/README.md',
        '/opt/mythos/notebooks/README.md',
    )
    if patch.errors: patch.finish(); return 1

    # ── 4. Set executable bits ───────────────────────────────────────────
    patch.logger.log("\n[4/8] Setting executable bits")
    ensure_executable(patch)
    if patch.errors: patch.finish(); return 1

    # ── 5. Ensure Jupyter token ──────────────────────────────────────────
    patch.logger.log("\n[5/8] Ensuring Jupyter token")
    ensure_jupyter_token(patch)
    if patch.errors: patch.finish(); return 1

    # ── 6. Deploy systemd unit (idempotent, NOT rollback-tracked) ────────
    patch.logger.log("\n[6/8] Deploying systemd unit")
    deploy_systemd_unit(patch)
    if patch.errors: patch.finish(); return 1

    # ── 7. Cloudflared ingress + DNS route ───────────────────────────────
    patch.logger.log("\n[7/8] Cloudflared ingress + DNS route")
    # Only touch cloudflared config if our rule isn't already there.
    # If we do touch it, we need to restart cloudflared. If we don't, skip.
    ingress_was_present = False
    try:
        existing = CLOUDFLARED_CONFIG.read_text()
        ingress_was_present = JUPYTER_HOSTNAME in existing
    except Exception:
        pass

    ensure_cloudflared_ingress(patch)
    if patch.errors: patch.finish(); return 1

    if not ingress_was_present and not patch.dry_run:
        # We just wrote to cloudflared config — restart to pick it up
        log(patch, "restarting cloudflared to pick up new ingress rule")
        try:
            run(["sudo", "systemctl", "restart", "--no-block", "cloudflared.service"])
            log_ok(patch, "restart cloudflared.service (async)")
        except subprocess.CalledProcessError as e:
            patch.errors.append(f"cloudflared restart: {e.stderr}")
        if not patch.errors:
            verify_cloudflared_active(patch)
        if patch.errors: patch.finish(); return 1
    else:
        log_skip(patch, "cloudflared restart not needed (config unchanged)")

    ensure_dns_route(patch)
    if patch.errors: patch.finish(); return 1

    # ── 8. Start mythos-jupyter and verify ───────────────────────────────
    patch.logger.log("\n[8/8] Starting mythos-jupyter and verifying")
    start_jupyter_and_verify(patch)

    # ── Post-patch summary ───────────────────────────────────────────────
    if not patch.errors and not patch.dry_run:
        try:
            token = TOKEN_FILE.read_text().strip()
            patch.logger.log("")
            patch.logger.log("=" * 55)
            patch.logger.log("  JUPYTER READY")
            patch.logger.log("=" * 55)
            patch.logger.log(f"  URL:     https://{JUPYTER_HOSTNAME}/lab?token={token}")
            patch.logger.log(f"  Local:   {JUPYTER_LOCAL_URL}")
            patch.logger.log(f"  Token:   {token}")
            patch.logger.log("")
            patch.logger.log("  Copy token:    jupyter-token --copy")
            patch.logger.log("  Rotate token:  jupyter-rotate-token")
            patch.logger.log("")
            patch.logger.log("  Next: run /opt/mythos/demo/prep_demo_graphs.sh")
            patch.logger.log("        to clone strapi and populate demo-complete.")
            patch.logger.log("=" * 55)
        except Exception as e:
            patch.logger.log(f"  (could not read token for summary: {e})")

    patch.finish()
    return 1 if patch.errors else 0


if __name__ == '__main__':
    sys.exit(main())

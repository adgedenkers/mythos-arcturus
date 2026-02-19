"""
Patch 0103: Version Enforcement
Patches mythos_patch_monitor.py to:
1. Read manifest.json for version instead of blind auto-increment
2. Update .version file after each patch
3. Use manifest version for git tag
"""
import re

MONITOR_PATH = '/opt/mythos/mythos_patch_monitor.py'

with open(MONITOR_PATH) as f:
    content = f.read()

# =============================================================
# FIX 1: Replace increment_version to read manifest first
# =============================================================

old_increment = '''    def increment_version(self, version: str) -> str:
        """Increment the patch version number"""
        match = re.match(r'v(\\d+)\\.(\\d+)\\.(\\d+)', version)
        if match:
            major, minor, patch = map(int, match.groups())
            return f"v{major}.{minor}.{patch + 1}"
        return "v1.0.0"'''

new_increment = '''    def increment_version(self, version: str) -> str:
        """Increment the patch version number (fallback when no manifest)"""
        match = re.match(r'v(\\d+)\\.(\\d+)\\.(\\d+)', version)
        if match:
            major, minor, patch = map(int, match.groups())
            return f"v{major}.{minor}.{patch + 1}"
        return "v1.0.0"

    def get_manifest_version(self, extract_dir) -> str:
        """Read version from manifest.json if present. Returns 'vX.Y.Z' or None."""
        import json as _json
        manifest_path = extract_dir / "manifest.json"
        if not manifest_path.exists():
            return None
        try:
            with open(manifest_path) as f:
                manifest = _json.load(f)
            # Try versioning.new_system_version first, then patch.semantic_version
            version = (
                manifest.get('versioning', {}).get('new_system_version')
                or manifest.get('patch', {}).get('semantic_version')
            )
            if version:
                if not version.startswith('v'):
                    version = f'v{version}'
                logger.info(f"Manifest version: {version}")
                return version
        except Exception as e:
            logger.warning(f"Could not read manifest version: {e}")
        return None

    def update_version_file(self, version: str):
        """Update /opt/mythos/.version with the current version."""
        version_str = version.lstrip('v')
        try:
            version_file = Path(MYTHOS_ROOT) / '.version'
            with open(version_file, 'w') as f:
                f.write(version_str + '\\n')
            logger.info(f"Updated .version to {version_str}")
        except Exception as e:
            logger.warning(f"Could not update .version file: {e}")'''

content = content.replace(old_increment, new_increment)

# =============================================================
# FIX 2: Update process_patch to use manifest version
# =============================================================

# Replace the git versioning block in process_patch
old_git_block = '''            # ---- GIT: Commit patch and tag new version ----
            if git_manager and git_manager.is_repo():
                current_version = git_manager.get_current_version()
                new_version = git_manager.increment_version(current_version)
                
                git_manager.commit_patch(name, files_in_zip)
                git_manager.tag_version(new_version, f"After applying {name}")
                
                # Push to GitHub if enabled
                if GITHUB_PUSH_ENABLED:
                    git_manager.push()
                
                logger.info(f"✓ Git versioned: {current_version} → {new_version}")'''

new_git_block = '''            # ---- GIT: Commit patch and tag new version ----
            if git_manager and git_manager.is_repo():
                current_version = git_manager.get_current_version()
                
                # Try manifest version first, fall back to auto-increment
                new_version = None
                if extract_dir:
                    new_version = git_manager.get_manifest_version(extract_dir)
                if not new_version:
                    new_version = git_manager.increment_version(current_version)
                    logger.warning(f"No manifest version found, auto-incremented to {new_version}")
                
                git_manager.commit_patch(name, files_in_zip)
                git_manager.tag_version(new_version, f"After applying {name}")
                
                # Update .version file
                git_manager.update_version_file(new_version)
                
                # Push to GitHub if enabled
                if GITHUB_PUSH_ENABLED:
                    git_manager.push()
                
                logger.info(f"✓ Git versioned: {current_version} → {new_version}")'''

content = content.replace(old_git_block, new_git_block)

# =============================================================
# FIX 3: Add install.sh chmod fix (ensure executable)
# Already has install_script.chmod(0o755) - verify
# =============================================================
# This is already in the code, so no change needed

# =============================================================
# Write
# =============================================================
with open(MONITOR_PATH, 'w') as f:
    f.write(content)

print("OK - patch monitor updated with manifest version reading")

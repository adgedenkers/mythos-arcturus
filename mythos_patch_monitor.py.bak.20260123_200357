#!/usr/bin/env python3
"""
Mythos Downloads Monitor Service - WITH GIT VERSIONING

Watches ~/Downloads for known artifact zip files and routes them to
appropriate handlers. Now includes automatic git snapshots before
applying patches and push to GitHub after.

Supported artifacts:
- patch_####_*.zip              → Mythos patch ingestion (with git versioning)
- sales-db-ingestion-####.zip   → Sales DB ingestion (stage + extract + run SQL)
- shoe-db-ingestion-####.zip    → Shoe DB ingestion (stage + extract + run SQL)

Git Integration:
- Creates tagged snapshot before applying any patch
- Commits changes after patch extraction
- Pushes to GitHub if remote is configured
- Supports rollback via git tags

Notes:
- Uses /opt/mythos/.venv python
- Executes SQL via the psql CLI through a dedicated runner script:
  /opt/mythos/sales_ingestion/ingest_sales_zip.py
"""

import os
import re
import shutil
import zipfile
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

WATCH_DIR = Path.home() / "Downloads"

MYTHOS_ROOT = Path("/opt/mythos")
PATCH_DIR = MYTHOS_ROOT / "patches"
PATCH_ARCHIVE_DIR = PATCH_DIR / "archive"
PATCH_LOG_DIR = PATCH_DIR / "logs"

SALES_DIR = Path("/opt/mythos/sales_ingestion")
SALES_ARCHIVE_DIR = SALES_DIR / "archive"

SHOE_DIR = Path("/opt/mythos/shoe_ingestion")
SHOE_ARCHIVE_DIR = SHOE_DIR / "archive"

INGESTOR = Path("/opt/mythos/sales_ingestion/ingest_sales_zip.py")
VENV_PY = Path("/opt/mythos/.venv/bin/python")

ARTIFACT_PATTERNS = {
    "patch": re.compile(r"^patch_\d{4}_.*\.zip$"),
    "sales_ingestion": re.compile(r"^sales-db-ingestion-\d{4}\.zip$"),
    "shoe_ingestion": re.compile(r"^shoe-db-ingestion-\d{4}\.zip$"),
}

# Git configuration
GIT_ENABLED = True
GITHUB_PUSH_ENABLED = True

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/var/log/mythos_patch_monitor.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("MythosDownloadsMonitor")

# ------------------------------------------------------------
# Git Operations
# ------------------------------------------------------------

class GitManager:
    """Handles git operations for patch versioning"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    def _run_git(self, *args, check=True) -> subprocess.CompletedProcess:
        """Run a git command in the repo directory"""
        cmd = ["git"] + list(args)
        logger.debug(f"Running: {' '.join(cmd)}")
        return subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=check
        )
    
    def is_repo(self) -> bool:
        """Check if directory is a git repo"""
        return (self.repo_path / ".git").is_dir()
    
    def has_remote(self) -> bool:
        """Check if remote origin is configured"""
        try:
            result = self._run_git("remote", "get-url", "origin", check=False)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_current_version(self) -> str:
        """Get the latest version tag or return v0.0.0"""
        try:
            result = self._run_git("tag", "-l", "v*", "--sort=-v:refname", check=False)
            tags = result.stdout.strip().split('\n')
            if tags and tags[0]:
                return tags[0]
        except Exception as e:
            logger.warning(f"Could not get version tags: {e}")
        return "v0.0.0"
    
    def increment_version(self, version: str) -> str:
        """Increment the patch version number"""
        match = re.match(r'v(\d+)\.(\d+)\.(\d+)', version)
        if match:
            major, minor, patch = map(int, match.groups())
            return f"v{major}.{minor}.{patch + 1}"
        return "v1.0.0"
    
    def has_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        try:
            result = self._run_git("status", "--porcelain", check=False)
            return bool(result.stdout.strip())
        except Exception:
            return False
    
    def create_snapshot(self, tag_name: str, message: str) -> bool:
        """Commit any changes and create a tagged snapshot"""
        try:
            # Stage all changes
            if self.has_changes():
                self._run_git("add", "-A")
                self._run_git("commit", "-m", f"Auto-commit before {tag_name}", check=False)
            
            # Create tag
            self._run_git("tag", "-a", tag_name, "-m", message, check=False)
            logger.info(f"Created git snapshot: {tag_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create snapshot: {e}")
            return False
    
    def commit_patch(self, patch_name: str, files_changed: list) -> bool:
        """Commit the patch changes"""
        try:
            self._run_git("add", "-A")
            
            files_str = ", ".join(files_changed[:5])
            if len(files_changed) > 5:
                files_str += f" (+{len(files_changed) - 5} more)"
            
            message = f"Applied patch: {patch_name}\n\nFiles: {files_str}"
            self._run_git("commit", "-m", message, check=False)
            logger.info(f"Committed patch: {patch_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to commit patch: {e}")
            return False
    
    def tag_version(self, version: str, message: str) -> bool:
        """Create a version tag"""
        try:
            self._run_git("tag", "-a", version, "-m", message, check=False)
            logger.info(f"Tagged version: {version}")
            return True
        except Exception as e:
            logger.error(f"Failed to tag version: {e}")
            return False
    
    def push(self) -> bool:
        """Push commits and tags to origin"""
        if not self.has_remote():
            logger.warning("No remote configured, skipping push")
            return False
        
        try:
            # Try main first, then master
            for branch in ["main", "master"]:
                result = self._run_git("push", "origin", branch, "--tags", check=False)
                if result.returncode == 0:
                    logger.info(f"Pushed to GitHub ({branch})")
                    return True
            
            logger.warning("Push failed - check remote configuration")
            return False
        except Exception as e:
            logger.error(f"Failed to push: {e}")
            return False
    
    def rollback_to_tag(self, tag: str) -> bool:
        """Rollback to a specific tag"""
        try:
            self._run_git("checkout", tag, "--", ".")
            logger.info(f"Rolled back to: {tag}")
            return True
        except Exception as e:
            logger.error(f"Failed to rollback: {e}")
            return False
    
    def list_tags(self, limit: int = 10) -> list:
        """List recent tags"""
        try:
            result = self._run_git("tag", "-l", "--sort=-v:refname", check=False)
            tags = result.stdout.strip().split('\n')
            return [t for t in tags if t][:limit]
        except Exception:
            return []


# Global git manager
git_manager = GitManager(MYTHOS_ROOT) if GIT_ENABLED else None

# ------------------------------------------------------------
# Handler
# ------------------------------------------------------------

class DownloadsHandler(FileSystemEventHandler):

    def __init__(self):
        super().__init__()
        self.processing = set()

    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)
        name = path.name

        artifact_type = self._detect_artifact_type(name)
        if not artifact_type:
            return

        logger.info(f"Detected {artifact_type} artifact: {name}")
        # Give browsers/OS time to finish writing the zip
        time.sleep(2)
        self.process_artifact(artifact_type, path)

    def _detect_artifact_type(self, filename):
        for artifact_type, pattern in ARTIFACT_PATTERNS.items():
            if pattern.match(filename):
                return artifact_type
        return None

    def process_artifact(self, artifact_type, path):
        if artifact_type == "patch":
            self.process_patch(path)
        elif artifact_type == "sales_ingestion":
            self.process_sales_ingestion(path)
        elif artifact_type == "shoe_ingestion":
            self.process_shoe_ingestion(path)

    # --------------------------------------------------------
    # Patch handling (with git versioning)
    # --------------------------------------------------------

    def process_patch(self, zip_path):
        name = zip_path.name
        if name in self.processing:
            return

        try:
            self.processing.add(name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if not self._is_valid_zip(zip_path):
                logger.error(f"Invalid patch zip: {name}")
                return

            PATCH_DIR.mkdir(parents=True, exist_ok=True)
            PATCH_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            PATCH_LOG_DIR.mkdir(parents=True, exist_ok=True)

            # ---- GIT: Create pre-patch snapshot ----
            if git_manager and git_manager.is_repo():
                pre_tag = f"pre-patch-{name.replace('.zip', '')}-{timestamp}"
                git_manager.create_snapshot(pre_tag, f"State before {name}")
                logger.info(f"✓ Git snapshot: {pre_tag}")

            # Copy zip to patches directory
            dest = PATCH_DIR / name
            shutil.copy2(zip_path, dest)

            # Extract
            extract_dir = None
            with zipfile.ZipFile(dest, "r") as z:
                # Get list of extracted files
                files_in_zip = z.namelist()
                z.extractall(PATCH_DIR)
                
                # Determine extract directory (usually the first directory in zip)
                for f in files_in_zip:
                    if '/' in f:
                        extract_dir = PATCH_DIR / f.split('/')[0]
                        break

            # Archive the zip
            shutil.move(dest, PATCH_ARCHIVE_DIR / name)
            
            # Remove original from Downloads
            zip_path.unlink()

            logger.info(f"✓ Patch extracted: {name}")
            if extract_dir:
                logger.info(f"  Extract location: {extract_dir}")

            # ---- GIT: Commit patch and tag new version ----
            if git_manager and git_manager.is_repo():
                current_version = git_manager.get_current_version()
                new_version = git_manager.increment_version(current_version)
                
                git_manager.commit_patch(name, files_in_zip)
                git_manager.tag_version(new_version, f"After applying {name}")
                
                # Push to GitHub if enabled
                if GITHUB_PUSH_ENABLED:
                    git_manager.push()
                
                logger.info(f"✓ Git versioned: {current_version} → {new_version}")

            # Log the patch application
            log_entry = {
                "timestamp": timestamp,
                "patch": name,
                "files": files_in_zip if 'files_in_zip' in dir() else [],
                "status": "success"
            }
            self._write_patch_log(log_entry)

            logger.info(f"✓ Patch processed: {name}")

        except Exception as e:
            logger.error(f"Patch error {name}: {e}", exc_info=True)
            self._write_patch_log({
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "patch": name,
                "status": "error",
                "error": str(e)
            })
        finally:
            self.processing.discard(name)

    def _write_patch_log(self, entry: dict):
        """Write patch application to log file"""
        import json
        log_file = PATCH_LOG_DIR / f"patch_{entry['timestamp']}.json"
        try:
            with open(log_file, 'w') as f:
                json.dump(entry, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write patch log: {e}")

    # --------------------------------------------------------
    # Sales ingestion handling
    # --------------------------------------------------------

    def process_sales_ingestion(self, zip_path):
        self._process_ingestion_zip(
            zip_path=zip_path,
            root_dir=SALES_DIR,
            archive_dir=SALES_ARCHIVE_DIR,
            ingestor_type="sales"
        )

    # --------------------------------------------------------
    # Shoe ingestion handling
    # --------------------------------------------------------

    def process_shoe_ingestion(self, zip_path):
        self._process_ingestion_zip(
            zip_path=zip_path,
            root_dir=SHOE_DIR,
            archive_dir=SHOE_ARCHIVE_DIR,
            ingestor_type="shoes"
        )

    # --------------------------------------------------------
    # Shared ingestion flow
    # --------------------------------------------------------

    def _process_ingestion_zip(self, zip_path: Path, root_dir: Path, archive_dir: Path, ingestor_type: str):
        name = zip_path.name
        if name in self.processing:
            return

        try:
            self.processing.add(name)

            if not self._is_valid_zip(zip_path):
                logger.error(f"Invalid {ingestor_type} ingestion zip: {name}")
                return

            root_dir.mkdir(parents=True, exist_ok=True)
            archive_dir.mkdir(parents=True, exist_ok=True)

            dest = root_dir / name
            shutil.copy2(zip_path, dest)

            extract_dir = root_dir / name.replace(".zip", "")
            extract_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(dest, "r") as z:
                z.extractall(extract_dir)

            # Archive the staged zip and remove the original download
            shutil.move(dest, archive_dir / name)
            zip_path.unlink()

            logger.info(f"✓ {ingestor_type} ingestion staged: {name} -> {extract_dir}")

            # Now run DB ingestion (SQL execution) via ingestor
            if not INGESTOR.exists():
                logger.error(f"Ingestor missing: {INGESTOR}. Staged only.")
                return
            if not VENV_PY.exists():
                logger.error(f"Venv python missing: {VENV_PY}. Staged only.")
                return

            env = os.environ.copy()
            # Default to mythos; allow override in service Environment or shell env
            env.setdefault("MYTHOS_DB", "mythos")

            cmd = [str(VENV_PY), str(INGESTOR), "--type", ingestor_type, "--extract-dir", str(extract_dir)]
            logger.info(f"Running ingestor: {' '.join(cmd)} (MYTHOS_DB={env.get('MYTHOS_DB')})")
            subprocess.run(cmd, check=True, env=env)

        except subprocess.CalledProcessError as e:
            logger.error(f"{ingestor_type} ingestion failed for {name}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"{ingestor_type} ingestion error {name}: {e}", exc_info=True)
        finally:
            self.processing.discard(name)

    # --------------------------------------------------------

    def _is_valid_zip(self, path):
        try:
            with zipfile.ZipFile(path, "r") as z:
                return z.testzip() is None
        except Exception:
            return False


# ------------------------------------------------------------
# Main loop
# ------------------------------------------------------------

def main():
    logger.info("=" * 60)
    logger.info("Mythos Downloads Monitor Service Starting")
    logger.info(f"Watching: {WATCH_DIR}")
    logger.info(f"Git enabled: {GIT_ENABLED}")
    logger.info(f"GitHub push enabled: {GITHUB_PUSH_ENABLED}")

    for k, v in ARTIFACT_PATTERNS.items():
        logger.info(f"Artifact type '{k}': {v.pattern}")

    # Check git status
    if git_manager:
        if git_manager.is_repo():
            logger.info(f"Git repo: {MYTHOS_ROOT}")
            logger.info(f"Current version: {git_manager.get_current_version()}")
            logger.info(f"Remote configured: {git_manager.has_remote()}")
        else:
            logger.warning(f"Not a git repo: {MYTHOS_ROOT}")

    logger.info("=" * 60)

    handler = DownloadsHandler()
    observer = Observer()
    observer.schedule(handler, str(WATCH_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()

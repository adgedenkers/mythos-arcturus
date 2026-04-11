#!/usr/bin/env python3
"""
Version Registry — Grid Node-Layer Version Management
=====================================================
Manages the version of each node-layer combination.
Supports:
  - Looking up current version for a node-layer
  - Detecting stale processing (exchange processed under old version)
  - Bumping versions when prompts change
  - Querying for exchanges that need reprocessing
"""

import os
import hashlib
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')
logger = logging.getLogger('grid.version_registry')

GRID_NODES = ['anchor', 'echo', 'beacon', 'synth', 'nexus', 'mirror', 'glyph', 'harmonia', 'gateway']
MAX_LAYERS = 9


def _get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor,
    )


class VersionRegistry:
    """Manages node-layer versions for the Arcturian Grid."""

    def __init__(self):
        self._cache: Dict[str, Dict] = {}
        self._cache_loaded = False

    def _load_cache(self):
        """Load all versions from Postgres into memory."""
        if self._cache_loaded:
            return
        try:
            conn = _get_conn()
            cur = conn.cursor()
            cur.execute("SELECT node, layer, version, prompt_hash, is_active FROM grid_version_registry")
            for row in cur.fetchall():
                key = f"{row['node']}:{row['layer']}"
                self._cache[key] = dict(row)
            cur.close()
            conn.close()
            self._cache_loaded = True
            logger.info(f"VersionRegistry: loaded {len(self._cache)} node-layer versions")
        except Exception as e:
            logger.error(f"VersionRegistry: failed to load cache: {e}")

    def get_version(self, node: str, layer: int) -> str:
        """Get the current version string for a node-layer."""
        self._load_cache()
        key = f"{node}:{layer}"
        entry = self._cache.get(key)
        if entry:
            return entry['version']
        return '0.0'  # Not yet registered

    def is_active(self, node: str, layer: int) -> bool:
        """Check if a node-layer is active (enabled for processing)."""
        self._load_cache()
        key = f"{node}:{layer}"
        entry = self._cache.get(key)
        if entry:
            return entry.get('is_active', False)
        return False

    def get_prompt_hash(self, node: str, layer: int) -> Optional[str]:
        """Get the stored prompt hash for a node-layer."""
        self._load_cache()
        key = f"{node}:{layer}"
        entry = self._cache.get(key)
        if entry:
            return entry.get('prompt_hash')
        return None

    def get_all_active(self, layer: int = None) -> List[Dict]:
        """Get all active node-layer entries, optionally filtered by layer."""
        self._load_cache()
        results = []
        for key, entry in self._cache.items():
            if not entry.get('is_active', False):
                continue
            if layer is not None and entry['layer'] != layer:
                continue
            results.append(entry)
        return results

    def bump_version(self, node: str, layer: int, new_version: str,
                     prompt_text: str = None, change_description: str = '') -> bool:
        """
        Bump the version of a node-layer.
        Records the change in the changelog.
        Busts the cache so next lookup gets the new version.
        """
        try:
            conn = _get_conn()
            cur = conn.cursor()

            prompt_hash = None
            if prompt_text:
                prompt_hash = hashlib.sha256(prompt_text.encode()).hexdigest()[:16]

            # Read current changelog
            cur.execute(
                "SELECT changelog FROM grid_version_registry WHERE node = %s AND layer = %s",
                (node, layer)
            )
            row = cur.fetchone()
            changelog = row['changelog'] if row else []
            if not isinstance(changelog, list):
                changelog = []

            changelog.append({
                'version': new_version,
                'date': datetime.now().isoformat(),
                'change': change_description,
            })

            cur.execute("""
                INSERT INTO grid_version_registry (node, layer, version, prompt_hash, changelog, updated_at)
                VALUES (%s, %s, %s, %s, %s::jsonb, NOW())
                ON CONFLICT (node, layer) DO UPDATE SET
                    version = EXCLUDED.version,
                    prompt_hash = EXCLUDED.prompt_hash,
                    changelog = %s::jsonb,
                    updated_at = NOW()
            """, (node, layer, new_version, prompt_hash,
                  psycopg2.extras.Json(changelog), psycopg2.extras.Json(changelog)))

            conn.commit()
            cur.close()
            conn.close()

            # Bust cache
            self._cache_loaded = False
            self._cache.clear()

            logger.info(f"VersionRegistry: bumped {node} L{layer} to {new_version}")
            return True
        except Exception as e:
            logger.error(f"VersionRegistry: bump failed: {e}")
            return False

    def find_stale_exchanges(self, node: str, layer: int,
                              old_version: str = None, limit: int = 100) -> List[Dict]:
        """
        Find exchanges processed under an older version of a node-layer.
        If old_version is None, finds anything not matching current version.
        Returns exchange_ids with their processing details.
        """
        current = self.get_version(node, layer)
        target_version = old_version or current

        try:
            conn = _get_conn()
            cur = conn.cursor()

            if old_version:
                # Find exchanges processed under a specific old version
                cur.execute("""
                    SELECT exchange_id, version, processed_at, extracted_count
                    FROM grid_processing_manifest
                    WHERE node = %s AND layer = %s AND version = %s AND activated = true
                    ORDER BY processed_at DESC
                    LIMIT %s
                """, (node, layer, old_version, limit))
            else:
                # Find exchanges NOT processed under current version
                cur.execute("""
                    SELECT exchange_id, version, processed_at, extracted_count
                    FROM grid_processing_manifest
                    WHERE node = %s AND layer = %s AND version != %s AND activated = true
                    ORDER BY processed_at DESC
                    LIMIT %s
                """, (node, layer, current, limit))

            results = [dict(r) for r in cur.fetchall()]
            cur.close()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"VersionRegistry: stale query failed: {e}")
            return []

    def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary of the version registry for diagnostics."""
        self._load_cache()
        summary = {
            'total_registered': len(self._cache),
            'active': sum(1 for e in self._cache.values() if e.get('is_active')),
            'nodes': {},
        }
        for key, entry in sorted(self._cache.items()):
            node = entry['node']
            if node not in summary['nodes']:
                summary['nodes'][node] = []
            summary['nodes'][node].append({
                'layer': entry['layer'],
                'version': entry['version'],
                'active': entry.get('is_active', False),
            })
        return summary

    @staticmethod
    def compute_prompt_hash(prompt_text: str) -> str:
        """Compute a short hash for a prompt string."""
        return hashlib.sha256(prompt_text.encode()).hexdigest()[:16]

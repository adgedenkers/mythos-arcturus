import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=10,
    description='person_intelligence_pipeline',
    patch_type='MAJOR',
)
patch.begin()

# ── Deploy new files ──────────────────────────────────────────────────

patch.deploy_file(
    'opt/mythos/iris/core/src/person_researcher.py',
    '/opt/mythos/iris/core/src/person_researcher.py',
)

patch.deploy_file(
    'opt/mythos/bin/iris-person',
    '/opt/mythos/bin/iris-person',
)

# Make CLI executable
import os
import stat
cli_path = '/opt/mythos/bin/iris-person'
os.chmod(cli_path, os.stat(cli_path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

# ── Run SQL migration ─────────────────────────────────────────────────

patch.run_sql('opt/mythos/migrations/neu_0010_person_research_trigger.sql')

# ── Modify context_engine.py — Add web_search + people_lookup providers ──

ce_path = '/opt/mythos/iris/core/src/context_engine.py'

with open(ce_path, 'r') as f:
    content = f.read()

# ── Edit 1: Add web_search and people_lookup to the provider registry ──

old_providers = '''            "env_sanitized": self._prov_env_sanitized,
        }'''

new_providers = '''            "env_sanitized": self._prov_env_sanitized,
            "web_search": self._prov_web_search,
            "people_lookup": self._prov_people_lookup,
            "person_research": self._prov_person_research,
        }'''

assert old_providers in content, f"Edit 1 FAILED: provider registry block not found in {ce_path}"
content = content.replace(old_providers, new_providers, 1)

# ── Edit 2: Add the three new provider methods before the ContextEngine class ──
# We add them at the end of the ContextProviders class, just before the
# ContextEngine class definition.

old_class_start = '''# ═══════════════════════════════════════════════════
# CONTEXT ENGINE — The orchestrator
# ═══════════════════════════════════════════════════'''

new_provider_methods = '''    def _prov_web_search(self, args: dict) -> str:
        """Search Wikipedia for a topic. Returns summary text."""
        query = args.get("query", "")
        if not query:
            raise ValueError("web_search provider requires 'query' arg")

        import urllib.parse
        import urllib.request

        # Wikipedia search
        params = urllib.parse.urlencode({
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": str(args.get("limit", 3)),
            "srprop": "snippet|titlesnippet",
        })
        url = f"https://en.wikipedia.org/w/api.php?{params}"

        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 Mythos/Iris ContextEngine"
            })
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read())
        except Exception as e:
            raise RuntimeError(f"Wikipedia search failed: {e}")

        results = data.get("query", {}).get("search", [])
        if not results:
            return f"No Wikipedia results for: {query}"

        lines = [f"Wikipedia results for '{query}':"]
        for res in results[:3]:
            title = res.get("title", "")
            snippet = re.sub(r'<[^>]+>', '', res.get("snippet", ""))
            lines.append(f"  • {title}: {snippet[:200]}")

        # Get summary of top result
        top_title = results[0].get("title", "")
        encoded = urllib.parse.quote(top_title.replace(" ", "_"))
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
        try:
            req = urllib.request.Request(summary_url, headers={
                "User-Agent": "Mozilla/5.0 Mythos/Iris ContextEngine"
            })
            with urllib.request.urlopen(req, timeout=8) as r:
                sdata = json.loads(r.read())
            extract = sdata.get("extract", "")
            if extract:
                lines.append(f"\\nSummary: {extract[:500]}")
        except Exception:
            pass

        return "\\n".join(lines)

    def _prov_people_lookup(self, args: dict) -> str:
        """Search the local people table by name."""
        name = args.get("name", "")
        if not name:
            raise ValueError("people_lookup provider requires 'name' arg")

        conn = psycopg2.connect(
            host="/var/run/postgresql",
            port=self.db_config.get("port", 5432),
            database=self.db_config.get("database", "mythos"),
            user=self.db_config.get("user", "adge"),
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
        conn.set_session(readonly=True, autocommit=True)
        try:
            cur = conn.cursor()
            search = name.strip().lower()
            cur.execute("""
                SELECT id, first_name, last_name, known_as, date_of_birth,
                       time_of_birth, birth_city, birth_state, birth_country,
                       date_of_death, canonical_id,
                       LEFT(notes, 300) as notes_preview
                FROM people
                WHERE LOWER(first_name) LIKE %s
                   OR LOWER(last_name) LIKE %s
                   OR LOWER(known_as) LIKE %s
                   OR LOWER(first_name || ' ' || last_name) LIKE %s
                ORDER BY last_name, first_name
                LIMIT 5
            """, (f"%{search}%",) * 4)
            rows = cur.fetchall()
            cur.close()
            if not rows:
                return f"No people found matching '{name}'"
            return json.dumps([dict(r) for r in rows], default=str, indent=2)
        finally:
            conn.close()

    def _prov_person_research(self, args: dict) -> str:
        """Research a person: local lookup first, then web if needed."""
        name = args.get("name", "")
        if not name:
            raise ValueError("person_research provider requires 'name' arg")

        try:
            from .person_researcher import research_person
            result = research_person(self.db_config, name, requested_by="context_engine")
            return json.dumps(result.person.to_dict(), default=str, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e), "name": name})


''' + '''# ═══════════════════════════════════════════════════
# CONTEXT ENGINE — The orchestrator
# ═══════════════════════════════════════════════════'''

assert old_class_start in content, f"Edit 2 FAILED: ContextEngine class header not found in {ce_path}"
content = content.replace(old_class_start, new_provider_methods, 1)

# ── Write modified file ──────────────────────────────────────────────

with open(ce_path, 'w') as f:
    f.write(content)

# ── Validate Python syntax ───────────────────────────────────────────

import py_compile
py_compile.compile(ce_path, doraise=True)
py_compile.compile('/opt/mythos/iris/core/src/person_researcher.py', doraise=True)
py_compile.compile('/opt/mythos/bin/iris-person', doraise=True)

print("✓ All Python files pass syntax check")

# ── Restart services ─────────────────────────────────────────────────

patch.restart_service('mythos-trigger.service')

patch.finish()

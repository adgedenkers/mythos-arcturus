#!/usr/bin/env python3
"""
Store — Save, load, and diff test results.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

RESULTS_DIR = Path(__file__).parent.parent / "results"


def ensure_results_dir():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def save_run(run_data: Dict[str, Any], tag: str = "") -> Path:
    """Save a test run to a timestamped JSON file. Returns the file path."""
    ensure_results_dir()
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    suffix = f"_{tag}" if tag else ""
    filename = f"run_{ts}{suffix}.json"
    path = RESULTS_DIR / filename

    with open(path, 'w') as f:
        json.dump(run_data, f, indent=2, default=str)

    return path


def load_run(path: str) -> Dict[str, Any]:
    """Load a saved run from JSON."""
    with open(path) as f:
        return json.load(f)


def list_runs(limit: int = 20) -> List[Dict[str, str]]:
    """List recent saved runs."""
    ensure_results_dir()
    files = sorted(RESULTS_DIR.glob("run_*.json"), reverse=True)
    runs = []
    for f in files[:limit]:
        try:
            with open(f) as fh:
                data = json.load(fh)
            runs.append({
                'file': f.name,
                'path': str(f),
                'timestamp': data.get('timestamp', '?'),
                'profile': data.get('profile', '?'),
                'model': data.get('model', '?'),
                'test_count': len(data.get('results', [])),
            })
        except Exception:
            runs.append({'file': f.name, 'path': str(f), 'error': 'parse failed'})
    return runs


def diff_runs(path_a: str, path_b: str) -> str:
    """Compare two runs and produce a human-readable diff."""
    a = load_run(path_a)
    b = load_run(path_b)

    lines = []
    lines.append(f"=== DIFF: {Path(path_a).name} vs {Path(path_b).name} ===")
    lines.append(f"A: profile={a.get('profile','?')} model={a.get('model','?')} personality={a.get('personality_preset','?')}")
    lines.append(f"B: profile={b.get('profile','?')} model={b.get('model','?')} personality={b.get('personality_preset','?')}")
    lines.append("")

    results_a = {r['test_id']: r for r in a.get('results', []) if 'test_id' in r}
    results_b = {r['test_id']: r for r in b.get('results', []) if 'test_id' in r}

    all_ids = sorted(set(list(results_a.keys()) + list(results_b.keys())))

    for test_id in all_ids:
        ra = results_a.get(test_id)
        rb = results_b.get(test_id)

        lines.append(f"--- {test_id} ---")

        if ra and rb:
            sa = ra.get('score', {}).get('score', '?')
            sb = rb.get('score', {}).get('score', '?')
            wa = ra.get('score', {}).get('word_count', '?')
            wb = rb.get('score', {}).get('word_count', '?')
            ta = ra.get('elapsed_seconds', '?')
            tb = rb.get('elapsed_seconds', '?')

            score_delta = ""
            if isinstance(sa, (int, float)) and isinstance(sb, (int, float)):
                d = sb - sa
                score_delta = f" ({'+' if d >= 0 else ''}{d})"

            lines.append(f"  Score:  A={sa}  B={sb}{score_delta}")
            lines.append(f"  Words:  A={wa}  B={wb}")
            lines.append(f"  Time:   A={ta}s  B={tb}s")

            # Penalty diff
            pa = set(ra.get('score', {}).get('penalties', []))
            pb = set(rb.get('score', {}).get('penalties', []))
            removed = pa - pb
            added = pb - pa
            if removed:
                lines.append(f"  Fixed in B: {', '.join(removed)}")
            if added:
                lines.append(f"  New in B: {', '.join(added)}")
        elif ra and not rb:
            lines.append(f"  Only in A (score={ra.get('score',{}).get('score','?')})")
        elif rb and not ra:
            lines.append(f"  Only in B (score={rb.get('score',{}).get('score','?')})")

        lines.append("")

    # Summary
    scores_a = [r.get('score', {}).get('score', 0) for r in results_a.values() if isinstance(r.get('score', {}).get('score'), (int, float))]
    scores_b = [r.get('score', {}).get('score', 0) for r in results_b.values() if isinstance(r.get('score', {}).get('score'), (int, float))]

    avg_a = sum(scores_a) / len(scores_a) if scores_a else 0
    avg_b = sum(scores_b) / len(scores_b) if scores_b else 0

    lines.append(f"AVERAGE SCORE: A={avg_a:.1f}  B={avg_b:.1f}  Delta={avg_b - avg_a:+.1f}")

    return "\n".join(lines)

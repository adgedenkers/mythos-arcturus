#!/usr/bin/env python3
"""
Benchmark Report Generator
============================
Reads a completed (or partial) benchmark run and produces a readable report.
Can be run while the benchmark is still in progress — reads what's there.

Usage:
    /opt/mythos/.venv/bin/python3 /opt/mythos/orchestrator/benchmark/report.py
    /opt/mythos/.venv/bin/python3 /opt/mythos/orchestrator/benchmark/report.py --run 20260307_214500_abc123
    /opt/mythos/.venv/bin/python3 /opt/mythos/orchestrator/benchmark/report.py --live
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BENCH_DIR = Path("/opt/mythos/orchestrator/benchmark")
RUNS_DIR = BENCH_DIR / "runs"


def load_latest_run() -> Path:
    runs = sorted(RUNS_DIR.iterdir(), key=lambda p: p.name, reverse=True)
    if not runs:
        print("No runs found.")
        sys.exit(1)
    return runs[0]


def load_jsonl(path: Path) -> list:
    records = []
    if not path.exists():
        return records
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass
    return records


def generate_report(run_dir: Path, live: bool = False):
    manifest_path = run_dir / "run_manifest.json"
    summary_path = run_dir / "run_summary.json"

    if not manifest_path.exists():
        print(f"No manifest found in {run_dir}")
        return

    with open(manifest_path) as f:
        manifest = json.load(f)

    models = manifest["models"]
    task_count = manifest["task_count"]
    started = manifest.get("started_at", "unknown")
    git_hash = manifest.get("git_hash", "unknown")

    results = load_jsonl(run_dir / "results.jsonl")
    scores = load_jsonl(run_dir / "judge_scores.jsonl")
    skips = load_jsonl(run_dir / "skips.jsonl")
    errors = load_jsonl(run_dir / "errors.jsonl")

    # Index
    results_idx = defaultdict(dict)
    for r in results:
        results_idx[r["model"]][r["task_id"]] = r

    scores_idx = defaultdict(dict)
    for s in scores:
        scores_idx[s["model"]][s["task_id"]] = s

    skip_idx = defaultdict(set)
    for s in skips:
        skip_idx[s["model"]].add(s["task_id"])

    error_idx = defaultdict(dict)
    for e in errors:
        error_idx[e["model"]][e["task_id"]] = e

    print("\n" + "="*70)
    print(f"  MYTHOS MODEL BENCHMARK REPORT")
    print(f"  Run: {run_dir.name}")
    print(f"  Started: {started}")
    print(f"  Git: {git_hash}")
    print(f"  Tasks: {task_count} | Models: {len(models)}")
    if live:
        completed = len(results) + len(skips) + len(errors)
        total = task_count * len(models)
        print(f"  Progress: {completed}/{total} ({completed/total*100:.0f}%) — LIVE VIEW")
    print("="*70)

    # ── Per-model summary ────────────────────────────────────────────────────
    print("\n  MODEL SUMMARY")
    print("  " + "-"*60)

    for model in models:
        res = results_idx[model]
        sco = scores_idx[model]
        skp = skip_idx[model]
        err = error_idx[model]

        n_pass = sum(1 for r in res.values() if r.get("status") == "pass")
        n_fail = sum(1 for r in res.values() if r.get("status") == "fail")
        n_skip = len(skp)
        n_timeout = sum(1 for e in err.values() if e.get("status") == "timeout")
        n_error = sum(1 for e in err.values() if e.get("status") == "error")

        total_score = sum(s.get("normalized_total", 0) or 0 for s in sco.values())
        max_score = sum(s.get("max_possible", 0) or 0 for s in sco.values())
        pct = f"{total_score/max_score*100:.1f}%" if max_score else "—"

        times = [r.get("response_ms", 0) for r in res.values() if r.get("response_ms")]
        avg_ms = f"{int(sum(times)/len(times))}ms" if times else "—"

        print(f"\n  {model}")
        print(f"    pass={n_pass}  fail={n_fail}  skip={n_skip}  timeout={n_timeout}  error={n_error}")
        print(f"    score={total_score}/{max_score} ({pct})  avg_response={avg_ms}")

    # ── Category breakdown ───────────────────────────────────────────────────
    categories = ["reasoning", "code", "mythos", "narrative", "tool_use", "voice"]
    print("\n\n  CATEGORY BREAKDOWN (pass rate)")
    print("  " + "-"*60)

    # Header
    header = f"  {'Category':12s}"
    for m in models:
        short = m.split(":")[0][:12]
        header += f"  {short:14s}"
    print(header)
    print("  " + "-"*60)

    for cat in categories:
        line = f"  {cat:12s}"
        for model in models:
            res = results_idx[model]
            cat_results = {tid: r for tid, r in res.items() if r.get("category") == cat}
            cat_scores = {tid: s for tid, s in scores_idx[model].items()
                         if any(r.get("category") == cat for r in results if r.get("task_id") == tid)}

            n_pass = sum(1 for r in cat_results.values() if r.get("status") == "pass")
            n_total = len(cat_results)
            score = sum(s.get("normalized_total", 0) or 0 for s in cat_scores.values())
            max_s = sum(s.get("max_possible", 0) or 0 for s in cat_scores.values())

            if n_total:
                pct = f"{n_pass}/{n_total}"
                score_str = f"({score}/{max_s})" if max_s else ""
                cell = f"{pct} {score_str}"
            else:
                cell = "—"
            line += f"  {cell:14s}"
        print(line)

    # ── Notable results ──────────────────────────────────────────────────────
    print("\n\n  NOTABLE RESULTS")
    print("  " + "-"*60)

    # Best single score
    best_score = None
    best_record = None
    for model in models:
        for tid, s in scores_idx[model].items():
            total = s.get("normalized_total")
            max_p = s.get("max_possible")
            if total is not None and max_p and total == max_p:
                print(f"  PERFECT SCORE: {tid} [{model}] — {total}/{max_p}")

    # Timeouts
    all_timeouts = [(e["model"], e["task_id"]) for e in errors if e.get("status") == "timeout"]
    if all_timeouts:
        print(f"\n  TIMEOUTS ({len(all_timeouts)}):")
        for model, tid in all_timeouts:
            print(f"    {tid} [{model}]")

    # Tasks where all models failed
    all_task_ids = {r["task_id"] for r in results}
    for tid in all_task_ids:
        all_failed = all(
            results_idx[m].get(tid, {}).get("status") in ("fail", None)
            for m in models
            if tid in results_idx[m]
        )
        if all_failed and all(tid in results_idx[m] for m in models):
            print(f"  ALL MODELS FAILED: {tid}")

    # ── Summary file note ────────────────────────────────────────────────────
    if summary_path.exists():
        with open(summary_path) as f:
            summary = json.load(f)
        ranking = summary.get("model_ranking", [])
        if ranking:
            print(f"\n\n  FINAL RANKING: {' > '.join(ranking)}")
            elapsed = summary.get("elapsed_seconds", 0)
            print(f"  Total runtime: {elapsed//3600}h {(elapsed%3600)//60}m {elapsed%60}s")
    else:
        print("\n\n  (run_summary.json not yet written — run still in progress or ended early)")

    print("\n" + "="*70)
    print(f"  Full results: {run_dir}/")
    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Benchmark Report Generator")
    parser.add_argument("--run", default=None, help="Run ID to report on (default: latest)")
    parser.add_argument("--live", action="store_true", help="Live view — report on in-progress run")
    args = parser.parse_args()

    if args.run:
        run_dir = RUNS_DIR / args.run
        if not run_dir.exists():
            print(f"Run not found: {run_dir}")
            sys.exit(1)
    else:
        run_dir = load_latest_run()

    if args.live:
        import time
        print(f"Live view mode — refreshing every 30s. Ctrl+C to exit.")
        while True:
            os.system("clear")
            generate_report(run_dir, live=True)
            try:
                time.sleep(30)
            except KeyboardInterrupt:
                break
    else:
        generate_report(run_dir)


if __name__ == "__main__":
    main()

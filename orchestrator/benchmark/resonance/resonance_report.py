#!/usr/bin/env python3
"""
Iris Resonance Benchmark — Phase 1 Report Generator
=====================================================
Reads Phase 1 results and produces:
1. Per-model resonance scores (weighted)
2. Per-model anti-pattern hit rates
3. Per-model response length analysis
4. Category breakdown
5. Model ranking with resonance pass/fail
6. Phase 2 grouping recommendation

Usage:
    /opt/mythos/.venv/bin/python3 resonance_report.py
    /opt/mythos/.venv/bin/python3 resonance_report.py --run 20260311_resonance
"""
import json
import sys
import argparse
from pathlib import Path
from collections import defaultdict

RUNS_DIR = Path("/opt/mythos/orchestrator/benchmark/resonance/runs")


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


def find_latest_run() -> Path:
    runs = sorted(RUNS_DIR.iterdir(), key=lambda p: p.name, reverse=True)
    if not runs:
        print("No runs found.")
        sys.exit(1)
    return runs[0]


def generate_report(run_dir: Path):
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"No manifest in {run_dir}")
        return

    with open(manifest_path) as f:
        manifest = json.load(f)

    results = load_jsonl(run_dir / "results.jsonl")
    scores = load_jsonl(run_dir / "judge_scores.jsonl")

    if not results:
        print("No results yet.")
        return

    # Index scores by (model, config, prompt_id)
    score_idx = {}
    for s in scores:
        key = (s["model"], s["config"], s["prompt_id"])
        score_idx[key] = s.get("scores", {})

    # ── Per-model aggregation ────────────────────────────────────────────────
    model_data = defaultdict(lambda: {
        "total_resonance": 0,
        "resonance_count": 0,
        "anti_pattern_hits": 0,
        "anti_pattern_checks": 0,
        "total_words": 0,
        "response_count": 0,
        "too_short": 0,
        "too_long": 0,
        "fabrication_fails": 0,
        "fabrication_checks": 0,
        "total_ms": 0,
        "errors": 0,
        "timeouts": 0,
        "categories": defaultdict(lambda: {"resonance_sum": 0, "count": 0}),
        "configs": defaultdict(lambda: {"resonance_sum": 0, "count": 0}),
        "dim_scores": defaultdict(lambda: {"sum": 0, "count": 0}),
    })

    WEIGHTS = {
        "voice_fidelity": 3,
        "energy_match": 2,
        "anti_pattern_avoidance": 3,
        "sovereign_alignment": 3,
        "response_richness": 2,
        "no_fabrication": 3,
    }

    for r in results:
        model = r["model"]
        md = model_data[model]

        if r["status"] == "timeout":
            md["timeouts"] += 1
            continue
        if r["status"] == "error":
            md["errors"] += 1
            continue

        md["response_count"] += 1
        md["total_words"] += r.get("word_count", 0)
        md["total_ms"] += r.get("elapsed_ms", 0)

        # Anti-pattern checks
        ap = r.get("anti_pattern_check", {})
        if ap:
            md["anti_pattern_checks"] += 1
            md["anti_pattern_hits"] += ap.get("hit_count", 0)

        # Length checks
        lc = r.get("length_check", {})
        if lc.get("too_short"):
            md["too_short"] += 1
        if lc.get("too_long"):
            md["too_long"] += 1

        # Fabrication
        fc = r.get("fabrication_check", {})
        if fc:
            md["fabrication_checks"] += 1
            if not fc.get("clean", True):
                md["fabrication_fails"] += 1

        # Judge scores
        key = (r["model"], r["config"], r["prompt_id"])
        s = score_idx.get(key, {})
        if s and "error" not in s:
            overall = s.get("overall_resonance", 0)
            if isinstance(overall, (int, float)):
                md["total_resonance"] += overall
                md["resonance_count"] += 1
                md["categories"][r["category"]]["resonance_sum"] += overall
                md["categories"][r["category"]]["count"] += 1
                md["configs"][r["config"]]["resonance_sum"] += overall
                md["configs"][r["config"]]["count"] += 1

                # Per-dimension
                for dim in WEIGHTS:
                    dim_data = s.get(dim, {})
                    if isinstance(dim_data, dict):
                        dim_score = dim_data.get("score", 0)
                        if isinstance(dim_score, (int, float)):
                            md["dim_scores"][dim]["sum"] += dim_score
                            md["dim_scores"][dim]["count"] += 1

    # ── PRINT REPORT ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  IRIS RESONANCE BENCHMARK — PHASE 1 REPORT")
    print(f"  Run: {run_dir.name}")
    print(f"  Models: {len(manifest.get('models', []))}")
    print(f"  Configs: {manifest.get('configs', [])}")
    print(f"  Prompts: {manifest.get('prompt_count', '?')}")
    print("=" * 70)

    # ── Model ranking ────────────────────────────────────────────────────────
    ranked = []
    for model, md in sorted(model_data.items()):
        avg_res = md["total_resonance"] / md["resonance_count"] if md["resonance_count"] else 0
        avg_words = md["total_words"] / md["response_count"] if md["response_count"] else 0
        avg_ms = md["total_ms"] / md["response_count"] if md["response_count"] else 0
        ap_rate = md["anti_pattern_hits"] / max(md["anti_pattern_checks"], 1)

        # Weighted dimension score
        weighted_total = 0
        weighted_max = 0
        for dim, w in WEIGHTS.items():
            ds = md["dim_scores"][dim]
            if ds["count"]:
                weighted_total += (ds["sum"] / ds["count"]) * w
                weighted_max += 3 * w

        weighted_pct = weighted_total / weighted_max * 100 if weighted_max else 0

        ranked.append({
            "model": model,
            "avg_resonance": avg_res,
            "weighted_pct": weighted_pct,
            "avg_words": avg_words,
            "avg_ms": avg_ms,
            "ap_rate": ap_rate,
            "ap_hits": md["anti_pattern_hits"],
            "too_short": md["too_short"],
            "too_long": md["too_long"],
            "fab_fails": md["fabrication_fails"],
            "responses": md["response_count"],
            "timeouts": md["timeouts"],
            "errors": md["errors"],
            "dim_scores": {
                dim: md["dim_scores"][dim]["sum"] / md["dim_scores"][dim]["count"]
                if md["dim_scores"][dim]["count"] else 0
                for dim in WEIGHTS
            },
            "categories": dict(md["categories"]),
            "configs": dict(md["configs"]),
        })

    ranked.sort(key=lambda x: x["weighted_pct"], reverse=True)

    print("\n  MODEL RANKING (by weighted resonance score)")
    print("  " + "-" * 66)
    print(f"  {'Model':<25s} {'Res/10':>7s} {'W.Score':>8s} {'Words':>6s} {'AP':>5s} {'Short':>5s} {'ms':>7s}")
    print("  " + "-" * 66)

    resonant_models = []
    non_resonant_models = []

    for r in ranked:
        # Resonance threshold: weighted score >= 60% AND avg resonance >= 6/10
        is_resonant = r["weighted_pct"] >= 60 and r["avg_resonance"] >= 6.0
        marker = "✓" if is_resonant else "✗"

        if is_resonant:
            resonant_models.append(r["model"])
        else:
            non_resonant_models.append(r["model"])

        print(f"  {marker} {r['model']:<23s} {r['avg_resonance']:>6.1f} {r['weighted_pct']:>7.1f}% "
              f"{r['avg_words']:>5.0f} {r['ap_hits']:>4d} {r['too_short']:>4d} {r['avg_ms']:>6.0f}")

    # ── Dimension breakdown ──────────────────────────────────────────────────
    print("\n\n  DIMENSION BREAKDOWN (avg score per model, max 3.0)")
    print("  " + "-" * 66)
    dims = list(WEIGHTS.keys())
    header = f"  {'Model':<22s}"
    for d in dims:
        short = d[:8]
        header += f" {short:>8s}"
    print(header)
    print("  " + "-" * 66)

    for r in ranked:
        line = f"  {r['model']:<22s}"
        for d in dims:
            score = r["dim_scores"].get(d, 0)
            line += f" {score:>8.1f}"
        print(line)

    # ── Category breakdown ───────────────────────────────────────────────────
    all_cats = set()
    for r in ranked:
        all_cats.update(r["categories"].keys())

    if all_cats:
        print("\n\n  CATEGORY BREAKDOWN (avg resonance per category)")
        print("  " + "-" * 66)
        cats = sorted(all_cats)
        header = f"  {'Model':<22s}"
        for c in cats:
            header += f" {c[:10]:>10s}"
        print(header)
        print("  " + "-" * 66)

        for r in ranked:
            line = f"  {r['model']:<22s}"
            for c in cats:
                cd = r["categories"].get(c, {})
                if cd.get("count"):
                    avg = cd["resonance_sum"] / cd["count"]
                    line += f" {avg:>10.1f}"
                else:
                    line += f" {'—':>10s}"
            print(line)

    # ── Phase 2 grouping ─────────────────────────────────────────────────────
    print(f"\n\n  PHASE 2 GROUPING")
    print("  " + "-" * 66)
    print(f"  RESONANT (proceed to Phase 3):")
    for m in resonant_models:
        print(f"    ✓ {m}")
    if not resonant_models:
        print("    (none)")

    print(f"\n  NON-RESONANT (second-tier testing):")
    for m in non_resonant_models:
        print(f"    ✗ {m}")
    if not non_resonant_models:
        print("    (none)")

    # ── Save machine-readable grouping ───────────────────────────────────────
    grouping = {
        "resonant": resonant_models,
        "non_resonant": non_resonant_models,
        "ranking": [r["model"] for r in ranked],
        "scores": {r["model"]: {"avg_resonance": r["avg_resonance"],
                                 "weighted_pct": r["weighted_pct"]}
                   for r in ranked},
    }
    with open(run_dir / "phase2_grouping.json", 'w') as f:
        json.dump(grouping, f, indent=2)

    print(f"\n  Grouping saved: {run_dir / 'phase2_grouping.json'}")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default=None)
    args = parser.parse_args()

    if args.run:
        run_dir = RUNS_DIR / args.run
    else:
        run_dir = find_latest_run()

    generate_report(run_dir)


if __name__ == "__main__":
    main()

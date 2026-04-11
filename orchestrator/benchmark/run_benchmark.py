#!/usr/bin/env python3
"""
Mythos Model Benchmark Harness
================================
Runs 43 tasks across 3 models. Dependency-aware, failure-tolerant,
incremental write-through to JSONL. Judge scoring after each result.
Leave it running, come back in the morning.

Usage:
    /opt/mythos/.venv/bin/python3 /opt/mythos/orchestrator/benchmark/run_benchmark.py
    /opt/mythos/.venv/bin/python3 /opt/mythos/orchestrator/benchmark/run_benchmark.py --skip-judge
    /opt/mythos/.venv/bin/python3 /opt/mythos/orchestrator/benchmark/run_benchmark.py --models gemma3:27b qwen2.5:32b
    /opt/mythos/.venv/bin/python3 /opt/mythos/orchestrator/benchmark/run_benchmark.py --tasks R-01 R-02 C-01

Output:
    /opt/mythos/orchestrator/benchmark/runs/{run_id}/
        run_manifest.json       — config + git hash + start time
        results.jsonl           — one line per task/model completion
        skips.jsonl             — dependency skips
        errors.jsonl            — exceptions + timeouts
        judge_scores.jsonl      — scoring results as they arrive
        run_summary.json        — written at end (model rankings, category breakdowns)
"""

import os
import sys
import json
import uuid
import time
import logging
import argparse
import threading
import subprocess
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

import requests

# ── Config ───────────────────────────────────────────────────────────────────

BENCH_DIR = Path("/opt/mythos/orchestrator/benchmark")
# CONFIG_PATH is now set in main() from --config arg (was hardcoded here — SYS-0034)

CONFIG = {}  # populated in main() from --config arg (SYS-0034)

sys.path.insert(0, str(BENCH_DIR))
from tasks import TASKS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("benchmark")

# ── JSONL Writer (thread-safe) ────────────────────────────────────────────────

class JSONLWriter:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    def write(self, record: dict):
        line = json.dumps(record, ensure_ascii=False, default=str)
        with self._lock:
            with open(self.path, "a") as f:
                f.write(line + "\n")
                f.flush()
                os.fsync(f.fileno())

# ── RunManager ───────────────────────────────────────────────────────────────

class RunManager:
    def __init__(self, run_id: str, models: List[str]):
        self.run_id = run_id
        self.models = models
        self.run_dir = BENCH_DIR / "runs" / run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.results   = JSONLWriter(self.run_dir / "results.jsonl")
        self.skips     = JSONLWriter(self.run_dir / "skips.jsonl")
        self.errors    = JSONLWriter(self.run_dir / "errors.jsonl")
        self.scores    = JSONLWriter(self.run_dir / "judge_scores.jsonl")

        git_hash = self._get_git_hash()

        manifest = {
            "run_id": run_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "models": models,
            "task_count": len(TASKS),
            "git_hash": git_hash,
            "config": CONFIG,
        }
        with open(self.run_dir / "run_manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

        log.info(f"Run {run_id} initialized → {self.run_dir}")

    def _get_git_hash(self) -> str:
        try:
            result = subprocess.run(
                ["git", "-C", "/opt/mythos", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() or "unknown"
        except Exception:
            return "unknown"

    def write_summary(self, summary: dict):
        with open(self.run_dir / "run_summary.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        log.info(f"Summary written → {self.run_dir / 'run_summary.json'}")

# ── Ollama Client ─────────────────────────────────────────────────────────────

def call_ollama(model: str, prompt: str, timeout: int) -> tuple[str, int, Optional[str]]:
    """
    Call Ollama with a single user prompt.
    Returns (response_text, response_ms, error_or_none)
    """
    start = time.time()
    try:
        resp = requests.post(
            f"{CONFIG['ollama_host']}/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {
                    "temperature": 0.4,
                    "num_predict": 4096,
                }
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data.get("message", {}).get("content", "")
        ms = int((time.time() - start) * 1000)
        return text, ms, None
    except requests.exceptions.Timeout:
        ms = int((time.time() - start) * 1000)
        return "", ms, f"TIMEOUT after {timeout}s"
    except Exception as e:
        ms = int((time.time() - start) * 1000)
        return "", ms, str(e)

# ── Judge Scorer ─────────────────────────────────────────────────────────────

JUDGE_SYSTEM = (
    "You are a precise scoring judge for an AI model benchmark. "
    "You will be given a task, a model's response, and a scoring rubric. "
    "Return ONLY a JSON object with these fields:\n"
    "{\n"
    "  \"accuracy\": 0-3,\n"
    "  \"format\": 0-3,\n"
    "  \"tone\": 0-3,\n"
    "  \"reasoning\": 0-3,\n"
    "  \"total\": 0-12,\n"
    "  \"notes\": \"one sentence explaining the scores\"\n"
    "}\n"
    "Only score dimensions listed in scoring_dims. Set others to -1 (not applicable). "
    "Be strict. 3 = perfect. 2 = good with minor gaps. 1 = partial. 0 = wrong/missing. "
    "OUTPUT ONLY THE JSON. No preamble, no markdown."
)

def judge_response(
    task: dict,
    model: str,
    response: str,
    run_manager: RunManager,
) -> dict:
    """Score a response using the judge model."""
    judge_model = CONFIG.get("judge_model", "gemma3:27b")

    judge_prompt = (
        f"TASK ID: {task['id']}\n"
        f"TASK TITLE: {task['title']}\n"
        f"SCORING DIMS: {task['scoring_dims']}\n\n"
        f"RUBRIC:\n{task['judge_rubric']}\n\n"
        f"MODEL BEING SCORED: {model}\n\n"
        f"MODEL RESPONSE:\n{response[:3000]}\n\n"
        f"Score the response per the rubric. Return only JSON."
    )

    full_prompt = JUDGE_SYSTEM + "\n\n" + judge_prompt
    judge_response_text, _, err = call_ollama(judge_model, full_prompt, timeout=60)

    score_record = {
        "task_id": task["id"],
        "model": model,
        "judge_model": judge_model,
        "scored_at": datetime.now(timezone.utc).isoformat(),
        "raw_judge_output": judge_response_text,
        "error": err,
    }

    if not err and judge_response_text:
        try:
            clean = judge_response_text.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            parsed = json.loads(clean.strip())
            score_record.update(parsed)
            # Normalize total — only sum applicable dims
            dims = task["scoring_dims"]
            total = sum(
                parsed.get(d, 0)
                for d in dims
                if isinstance(parsed.get(d), (int, float)) and parsed.get(d) >= 0
            )
            score_record["normalized_total"] = total
            score_record["max_possible"] = len(dims) * 3
        except Exception as e:
            score_record["parse_error"] = str(e)

    run_manager.scores.write(score_record)
    return score_record

# ── Dependency Resolver ───────────────────────────────────────────────────────

class DependencyResolver:
    """
    Per-model dependency tracking.
    A task is runnable for a model when all its depends_on tasks
    have a PASS result for that model.
    """
    def __init__(self, tasks: List[dict], models: List[str]):
        self.tasks = {t["id"]: t for t in tasks}
        self.models = models
        # result_status[model][task_id] = "pass" | "fail" | "skip" | "timeout"
        self.result_status: Dict[str, Dict[str, str]] = {m: {} for m in models}
        self._lock = threading.Lock()

    def record_result(self, model: str, task_id: str, status: str):
        with self._lock:
            self.result_status[model][task_id] = status

    def is_runnable(self, model: str, task_id: str) -> bool:
        task = self.tasks[task_id]
        with self._lock:
            for dep_id in task.get("depends_on", []):
                dep_status = self.result_status[model].get(dep_id)
                if dep_status != "pass":
                    return False
        return True

    def should_skip(self, model: str, task_id: str) -> Optional[str]:
        """
        Returns the reason to skip, or None if should run.
        A task should be skipped if any dependency failed/was skipped/timed out.
        """
        task = self.tasks[task_id]
        with self._lock:
            for dep_id in task.get("depends_on", []):
                dep_status = self.result_status[model].get(dep_id)
                if dep_status in ("fail", "skip", "timeout", "error"):
                    return f"upstream {dep_id} had status={dep_status}"
                if dep_status is None:
                    return f"upstream {dep_id} not yet complete"
        return None

    def all_deps_resolved(self, model: str, task_id: str) -> bool:
        """All dependencies have some terminal status (not pending)."""
        task = self.tasks[task_id]
        with self._lock:
            for dep_id in task.get("depends_on", []):
                if dep_id not in self.result_status[model]:
                    return False
        return True

# ── Task Runner ───────────────────────────────────────────────────────────────

def run_task_for_model(
    task: dict,
    model: str,
    run_manager: RunManager,
    resolver: DependencyResolver,
    judge_enabled: bool,
) -> str:
    """
    Run a single task for a single model.
    Returns status: "pass" | "fail" | "timeout" | "error" | "skip"
    """
    task_id = task["id"]
    timeout = CONFIG["timeouts"].get(task["timeout_key"], CONFIG["timeouts"]["default"])

    # Check for skip
    skip_reason = resolver.should_skip(model, task_id)
    if skip_reason:
        run_manager.skips.write({
            "task_id": task_id,
            "model": model,
            "reason": skip_reason,
            "skipped_at": datetime.now(timezone.utc).isoformat(),
        })
        resolver.record_result(model, task_id, "skip")
        log.info(f"  SKIP  {task_id} [{model}] — {skip_reason}")
        return "skip"

    log.info(f"  RUN   {task_id} [{model}] (timeout={timeout}s)")

    response_text, response_ms, error = call_ollama(model, task["prompt"], timeout)

    if error:
        status = "timeout" if "TIMEOUT" in error else "error"
        run_manager.errors.write({
            "task_id": task_id,
            "model": model,
            "error": error,
            "response_ms": response_ms,
            "status": status,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        })
        resolver.record_result(model, task_id, status)
        log.warning(f"  {status.upper()} {task_id} [{model}] — {error}")
        return status

    # Check expected keywords for basic pass/fail
    keywords = task.get("expected_keywords", [])
    response_lower = response_text.lower()
    keyword_hit = (
        not keywords or
        any(kw.lower() in response_lower for kw in keywords)
    )
    status = "pass" if keyword_hit else "fail"

    result_record = {
        "task_id": task_id,
        "category": task["category"],
        "title": task["title"],
        "model": model,
        "status": status,
        "response_ms": response_ms,
        "response_length": len(response_text),
        "keyword_hit": keyword_hit,
        "keywords_checked": keywords,
        "response": response_text[:8000],  # cap for storage
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    run_manager.results.write(result_record)
    resolver.record_result(model, task_id, status)

    log.info(
        f"  {'PASS' if status == 'pass' else 'FAIL'}  "
        f"{task_id} [{model}] — {response_ms}ms, {len(response_text)} chars"
    )

    # Judge scoring (non-blocking — runs in same thread after result is written)
    if judge_enabled and CONFIG.get("judge_enabled", True):
        try:
            score = judge_response(task, model, response_text, run_manager)
            total = score.get("normalized_total", "?")
            max_p = score.get("max_possible", "?")
            log.info(f"  SCORE {task_id} [{model}] — {total}/{max_p}")
        except Exception as e:
            log.warning(f"  Judge failed for {task_id} [{model}]: {e}")

    return status

# ── Benchmark Orchestrator ────────────────────────────────────────────────────

def build_execution_waves(tasks: List[dict], task_ids: Set[str]) -> List[List[dict]]:
    """
    Topological sort → execution waves.
    Wave 0 = no dependencies. Wave N = all deps in waves 0..N-1.
    Each wave can run fully in parallel (across tasks × models).
    """
    task_map = {t["id"]: t for t in tasks if t["id"] in task_ids}
    remaining = set(task_map.keys())
    completed = set()
    waves = []

    while remaining:
        wave = []
        for tid in list(remaining):
            task = task_map[tid]
            deps = [d for d in task.get("depends_on", []) if d in task_ids]
            if all(d in completed for d in deps):
                wave.append(task_map[tid])

        if not wave:
            # Circular dependency or unresolvable — add remaining as final wave
            log.error(f"Dependency deadlock — forcing remaining tasks: {remaining}")
            wave = [task_map[tid] for tid in remaining]

        waves.append(wave)
        for t in wave:
            remaining.discard(t["id"])
            completed.add(t["id"])

    return waves

def run_benchmark(
    models: List[str],
    task_filter: Optional[List[str]],
    judge_enabled: bool,
):
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    run_manager = RunManager(run_id, models)

    # Filter tasks
    skip_ids = set(CONFIG.get("skip_task_ids", []))
    all_tasks = [t for t in TASKS if t["id"] not in skip_ids]
    if task_filter:
        all_tasks = [t for t in all_tasks if t["id"] in task_filter]

    task_ids = {t["id"] for t in all_tasks}
    resolver = DependencyResolver(all_tasks, models)

    log.info(f"Starting benchmark run {run_id}")
    log.info(f"Models: {models}")
    log.info(f"Tasks: {len(all_tasks)} | Judge: {judge_enabled}")

    waves = build_execution_waves(all_tasks, task_ids)
    log.info(f"Execution waves: {len(waves)} (wave sizes: {[len(w) for w in waves]})")

    total_tasks = len(all_tasks) * len(models)
    completed_count = 0
    all_start = time.time()

    max_workers = CONFIG.get("max_model_threads", 3)

    for wave_num, wave in enumerate(waves):
        log.info(f"\n{'='*60}")
        log.info(f"WAVE {wave_num + 1}/{len(waves)} — {len(wave)} tasks × {len(models)} models")
        log.info(f"{'='*60}")

        # Each wave: run all (task × model) combinations in parallel
        futures: List[tuple] = []

        with ThreadPoolExecutor(max_workers=max_workers * len(wave)) as executor:
            for task in wave:
                for model in models:
                    future = executor.submit(
                        run_task_for_model,
                        task, model, run_manager, resolver, judge_enabled
                    )
                    futures.append((future, task["id"], model))

            for future, task_id, model in futures:
                try:
                    status = future.result()
                    completed_count += 1
                    elapsed = time.time() - all_start
                    pct = (completed_count / total_tasks) * 100
                    log.info(
                        f"  [{completed_count}/{total_tasks} {pct:.0f}%] "
                        f"{task_id}/{model} = {status} "
                        f"(elapsed {elapsed/60:.1f}m)"
                    )
                except Exception as e:
                    log.error(f"  EXCEPTION {task_id}/{model}: {e}")
                    resolver.record_result(model, task_id, "error")
                    run_manager.errors.write({
                        "task_id": task_id,
                        "model": model,
                        "error": str(e),
                        "status": "error",
                        "occurred_at": datetime.now(timezone.utc).isoformat(),
                    })

    # ── Generate summary ─────────────────────────────────────────────────────
    log.info("\n" + "="*60)
    log.info("Generating run summary...")

    summary = _build_summary(run_id, run_manager, models, all_tasks, all_start)
    run_manager.write_summary(summary)

    # Print top-line results
    log.info("\n" + "="*60)
    log.info("BENCHMARK COMPLETE")
    log.info("="*60)
    for model in models:
        stats = summary["per_model"].get(model, {})
        log.info(
            f"  {model}: "
            f"pass={stats.get('pass', 0)} "
            f"fail={stats.get('fail', 0)} "
            f"skip={stats.get('skip', 0)} "
            f"timeout={stats.get('timeout', 0)} "
            f"score={stats.get('total_score', '?')}/{stats.get('max_score', '?')}"
        )
    log.info(f"\nResults: {run_manager.run_dir}")


def _build_summary(
    run_id: str,
    run_manager: RunManager,
    models: List[str],
    tasks: List[dict],
    start_time: float,
) -> dict:
    """Read all JSONL files and build summary."""
    elapsed_seconds = int(time.time() - start_time)

    # Load results
    results_by_model_task: Dict[str, Dict[str, dict]] = {m: {} for m in models}
    results_path = run_manager.run_dir / "results.jsonl"
    if results_path.exists():
        with open(results_path) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    results_by_model_task[r["model"]][r["task_id"]] = r
                except Exception:
                    pass

    # Load scores
    scores_by_model_task: Dict[str, Dict[str, dict]] = {m: {} for m in models}
    scores_path = run_manager.run_dir / "judge_scores.jsonl"
    if scores_path.exists():
        with open(scores_path) as f:
            for line in f:
                try:
                    s = json.loads(line)
                    scores_by_model_task[s["model"]][s["task_id"]] = s
                except Exception:
                    pass

    # Load skips and errors
    skip_count: Dict[str, int] = {m: 0 for m in models}
    skips_path = run_manager.run_dir / "skips.jsonl"
    if skips_path.exists():
        with open(skips_path) as f:
            for line in f:
                try:
                    s = json.loads(line)
                    skip_count[s["model"]] = skip_count.get(s["model"], 0) + 1
                except Exception:
                    pass

    # Build per-model stats
    categories = list({t["category"] for t in tasks})
    per_model = {}
    for model in models:
        model_results = results_by_model_task[model]
        model_scores = scores_by_model_task[model]

        status_counts = {"pass": 0, "fail": 0, "timeout": 0, "error": 0, "skip": skip_count.get(model, 0)}
        for r in model_results.values():
            status_counts[r.get("status", "error")] = status_counts.get(r.get("status", "error"), 0) + 1

        total_score = 0
        max_score = 0
        for task in tasks:
            if task["id"] in model_scores:
                s = model_scores[task["id"]]
                total_score += s.get("normalized_total", 0) or 0
                max_score += s.get("max_possible", len(task["scoring_dims"]) * 3)

        # Per-category breakdown
        cat_breakdown = {}
        for cat in categories:
            cat_tasks = [t for t in tasks if t["category"] == cat]
            cat_pass = sum(
                1 for t in cat_tasks
                if model_results.get(t["id"], {}).get("status") == "pass"
            )
            cat_score = sum(
                model_scores.get(t["id"], {}).get("normalized_total", 0) or 0
                for t in cat_tasks
            )
            cat_max = sum(
                (model_scores.get(t["id"], {}).get("max_possible") or len(t["scoring_dims"]) * 3)
                for t in cat_tasks
            )
            cat_breakdown[cat] = {
                "pass": cat_pass,
                "total_tasks": len(cat_tasks),
                "score": cat_score,
                "max": cat_max,
            }

        # Avg response time
        times = [r.get("response_ms", 0) for r in model_results.values() if r.get("response_ms")]
        avg_ms = int(sum(times) / len(times)) if times else 0

        per_model[model] = {
            **status_counts,
            "total_score": total_score,
            "max_score": max_score,
            "score_pct": round((total_score / max_score * 100), 1) if max_score else 0,
            "avg_response_ms": avg_ms,
            "category_breakdown": cat_breakdown,
        }

    # Rank models by total score
    ranked = sorted(
        models,
        key=lambda m: per_model[m].get("score_pct", 0),
        reverse=True
    )

    return {
        "run_id": run_id,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed_seconds,
        "task_count": len(tasks),
        "model_count": len(models),
        "per_model": per_model,
        "model_ranking": ranked,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    global CONFIG, CONFIG_PATH
    parser = argparse.ArgumentParser(description="Mythos Model Benchmark Harness")
    parser.add_argument('--config', type=str, default='bench_config.json',
                    help='Path to benchmark config JSON')
    parser.add_argument(
        "--models", nargs="+",
        default=None,
        help="Models to benchmark (space-separated)"
    )
    parser.add_argument(
        "--tasks", nargs="+",
        default=None,
        help="Run only specific task IDs (space-separated)"
    )
    parser.add_argument(
        "--skip-judge", action="store_true",
        help="Skip judge scoring (faster, raw results only)"
    )
    parser.add_argument(
        "--list-tasks", action="store_true",
        help="Print all task IDs and exit"
    )
    args = parser.parse_args()

    # SYS-0034: load config from --config arg (was hardcoded at module level)
    CONFIG_PATH = BENCH_DIR / args.config
    if not CONFIG_PATH.exists():
        print(f"ERROR: Config file not found: {CONFIG_PATH}")
        sys.exit(1)
    CONFIG = json.loads(CONFIG_PATH.read_text())
    print(f"  Loaded config: {CONFIG_PATH.name}")
    print(f"  Models: {CONFIG.get('models', [])}")
    # If --models not passed, use config file models
    if not args.models:
        args.models = CONFIG.get("models", [])


    if args.list_tasks:
        for t in TASKS:
            deps = ", ".join(t["depends_on"]) if t["depends_on"] else "none"
            print(f"  {t['id']:8s}  [{t['category']:10s}]  {t['title']} (deps: {deps})")
        return

    run_benchmark(
        models=args.models,
        task_filter=args.tasks,
        judge_enabled=not args.skip_judge,
    )


if __name__ == "__main__":
    main()

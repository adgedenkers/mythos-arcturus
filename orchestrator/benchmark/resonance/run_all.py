#!/usr/bin/env python3
"""
Iris Resonance Benchmark — Master Runner
==========================================
Runs all 4 phases in sequence. Can be run overnight.

Phase 1: Resonance screening (all models × 2 configs × 16 prompts)
Phase 2: Auto-sort models into resonant/non-resonant groups
Phase 3: Position testing (resonant models only)
Phase 4: Padding experiment (top 3 resonant models only)

Usage:
    /opt/mythos/.venv/bin/python3 run_all.py
    /opt/mythos/.venv/bin/python3 run_all.py --phase1-only
    /opt/mythos/.venv/bin/python3 run_all.py --skip-phase1
"""
import sys
import argparse
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/opt/mythos/orchestrator/benchmark/resonance/benchmark.log'),
    ]
)
log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Iris Resonance Benchmark — Full Run")
    parser.add_argument("--phase1-only", action="store_true", help="Run only Phase 1")
    parser.add_argument("--skip-phase1", action="store_true", help="Skip Phase 1 (use existing results)")
    parser.add_argument("--skip-phase3", action="store_true")
    parser.add_argument("--skip-phase4", action="store_true")
    parser.add_argument("--models", nargs="+", help="Override model list for all phases")
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("  IRIS RESONANCE BENCHMARK — FULL RUN")
    log.info(f"  Started: {datetime.now().isoformat()}")
    log.info("=" * 60)

    # ── PHASE 1 ──
    if not args.skip_phase1:
        log.info("\n\n" + "=" * 60)
        log.info("  PHASE 1: RESONANCE SCREENING")
        log.info("=" * 60)
        from run_phase1 import run_phase1
        run_phase1(
            models=args.models,
            configs=["full_iris", "identity_only", "full_iris_verbose"],
        )

        # Generate report (which also creates phase2_grouping.json)
        log.info("\nGenerating Phase 1 report...")
        from resonance_report import find_latest_run, generate_report
        run_dir = find_latest_run()
        generate_report(run_dir)
    else:
        log.info("Skipping Phase 1 (--skip-phase1)")

    if args.phase1_only:
        log.info("Phase 1 only mode — stopping here.")
        return

    # ── PHASE 3 ──
    if not args.skip_phase3:
        log.info("\n\n" + "=" * 60)
        log.info("  PHASE 3: PROMPT POSITION TESTING")
        log.info("=" * 60)
        from run_phase3 import run_phase3
        run_phase3(models=args.models)
    else:
        log.info("Skipping Phase 3")

    # ── PHASE 4 ──
    if not args.skip_phase4:
        log.info("\n\n" + "=" * 60)
        log.info("  PHASE 4: PADDING/SCAFFOLDING EXPERIMENT")
        log.info("=" * 60)
        from run_phase4 import run_phase4
        run_phase4(models=args.models)
    else:
        log.info("Skipping Phase 4")

    log.info("\n\n" + "=" * 60)
    log.info("  ALL PHASES COMPLETE")
    log.info(f"  Finished: {datetime.now().isoformat()}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()

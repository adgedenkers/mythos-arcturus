#!/usr/bin/env python3
"""
LOG-0014: Mythos Model Benchmark Harness
==========================================
Deploys the benchmark harness to /opt/mythos/orchestrator/benchmark/.
Creates the runs/ directory. Installs the 'mythos-bench' CLI tool.

No services restarted — benchmark runs on demand.
"""
import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=14,
    description='model_benchmark_harness',
    patch_type='MINOR',
)
patch.begin()

# Deploy benchmark files
patch.deploy_file(
    'opt/mythos/orchestrator/benchmark/bench_config.json',
    '/opt/mythos/orchestrator/benchmark/bench_config.json',
)
patch.deploy_file(
    'opt/mythos/orchestrator/benchmark/tasks.py',
    '/opt/mythos/orchestrator/benchmark/tasks.py',
)
patch.deploy_file(
    'opt/mythos/orchestrator/benchmark/run_benchmark.py',
    '/opt/mythos/orchestrator/benchmark/run_benchmark.py',
)
patch.deploy_file(
    'opt/mythos/orchestrator/benchmark/report.py',
    '/opt/mythos/orchestrator/benchmark/report.py',
)

# Create runs directory
runs_dir = '/opt/mythos/orchestrator/benchmark/runs'
os.makedirs(runs_dir, exist_ok=True)

# Make scripts executable
import stat
for script in ['run_benchmark.py', 'report.py']:
    path = f'/opt/mythos/orchestrator/benchmark/{script}'
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

# Install CLI symlinks to /opt/mythos/bin/
bin_dir = '/opt/mythos/bin'
os.makedirs(bin_dir, exist_ok=True)

for link_name, target in [
    ('mythos-bench', '/opt/mythos/orchestrator/benchmark/run_benchmark.py'),
    ('mythos-bench-report', '/opt/mythos/orchestrator/benchmark/report.py'),
]:
    link_path = f'{bin_dir}/{link_name}'
    if os.path.islink(link_path):
        os.unlink(link_path)
    os.symlink(target, link_path)

patch.finish()

print("\n✓ Benchmark harness installed")
print("  Run:    mythos-bench")
print("  Report: mythos-bench-report")
print("  Live:   mythos-bench-report --live")
print(f"\n  Results will be written to: {runs_dir}/")

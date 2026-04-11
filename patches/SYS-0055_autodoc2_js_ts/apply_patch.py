#!/usr/bin/env python3
"""
SYS-0055_autodoc2_js_ts

Phase 2: JavaScript and TypeScript walkers for AutoDoc2.

Adds:
  - walkers/javascript_walker.py    JS / JSX / MJS / CJS support
  - walkers/typescript_walker.py    TypeScript and TSX support
  - Updated walkers/__init__.py     registers JS, TS, TSX walkers
  - Updated filters.py              routes .tsx to its own grammar key,
                                    skips .d.ts declaration files

Pre-warms the JS / TS / TSX grammars during install so first-crawl-time
on a sandboxed network won't trigger surprise downloads.

This version (re-issued after a smoke-test syntax error in the previous
attempt) writes verification scripts to tempfiles instead of cramming
multi-line Python into `python -c` one-liners — `python -c` rejects
compound statements like `for` loops on a single line.
"""

import sys
import subprocess
import tempfile
import os
import textwrap

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

VENV_PY = '/opt/mythos/.venv/bin/python3'

patch = PatchBase(
    stream='SYS',
    number=55,
    description='autodoc2_js_ts',
    patch_type='MINOR',
)
patch.begin()

# 1. Deploy walker files and updated registry/filters
files_to_deploy = [
    'opt/mythos/tools/autodoc2/filters.py',
    'opt/mythos/tools/autodoc2/walkers/__init__.py',
    'opt/mythos/tools/autodoc2/walkers/javascript_walker.py',
    'opt/mythos/tools/autodoc2/walkers/typescript_walker.py',
]
for relpath in files_to_deploy:
    patch.deploy_file(relpath, '/' + relpath)


def run_python_script(label, script_body):
    """Write script_body to a tempfile and execute it via the venv Python.
    Avoids the `python -c` one-liner trap (no compound statements allowed)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(textwrap.dedent(script_body))
        script_path = f.name
    try:
        result = subprocess.run(
            [VENV_PY, script_path],
            check=True, capture_output=True, text=True,
        )
        for line in result.stdout.strip().split('\n'):
            print(f"[autodoc2_js_ts] {line}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[autodoc2_js_ts] FAILED: {label}")
        if e.stdout:
            print(f"      stdout: {e.stdout}")
        if e.stderr:
            print(f"      stderr: {e.stderr}")
        return False
    finally:
        os.unlink(script_path)


# 2. Pre-warm grammars
print("[autodoc2_js_ts] Pre-warming JavaScript / TypeScript / TSX grammars...")
ok = run_python_script("grammar pre-warm", """
    from tree_sitter_language_pack import get_parser

    jp = get_parser("javascript")
    tp = get_parser("typescript")
    xp = get_parser("tsx")

    js  = jp.parse(b"function f(){return 1}")
    ts  = tp.parse(b"interface I { x: number }")
    tsx = xp.parse(b"const C = () => <div/>;")

    print("javascript root:", js.root_node.type, "children:", len(js.root_node.children))
    print("typescript root:", ts.root_node.type, "children:", len(ts.root_node.children))
    print("tsx root:", tsx.root_node.type, "children:", len(tsx.root_node.children))
""")
if not ok:
    sys.exit(1)

# 3. Smoke-test the registry
print("[autodoc2_js_ts] Smoke-testing walker registry...")
ok = run_python_script("registry smoke test", """
    import sys
    sys.path.insert(0, "/opt/mythos/tools")
    from autodoc2.walkers import get_walker, supported_languages

    langs = supported_languages()
    print("languages:", langs)
    for L in langs:
        w = get_walker(L)
        grammar_key = getattr(w, "grammar_key", "-")
        print(f"  {L}: {w.__class__.__name__} available={w._available} grammar_key={grammar_key}")
""")
if not ok:
    sys.exit(1)

# 4. Functional smoke test — actually parse a tiny snippet through each walker
print("[autodoc2_js_ts] Functional smoke test (parse snippets through walkers)...")
ok = run_python_script("functional smoke test", """
    import sys
    from pathlib import Path
    sys.path.insert(0, "/opt/mythos/tools")
    from autodoc2.walkers import get_walker

    JS_SRC = b'''
    import { foo } from './bar';
    export class Queue {
        constructor() { this.items = []; }
        async push(x) { this.items.push(x); }
    }
    const helper = () => 42;
    '''

    TS_SRC = b'''
    import { z } from 'zod';
    export interface User { name: string; age: number; }
    export type ID = string | number;
    export class Service {
        async getUser(id: ID): Promise<User> { return {name: '', age: 0}; }
    }
    '''

    TSX_SRC = b'''
    import React from 'react';
    interface Props { name: string }
    export const Hello = ({name}: Props) => <div>Hello {name}</div>;
    '''

    cases = [
        ('javascript', 'demo.js',  JS_SRC),
        ('typescript', 'demo.ts',  TS_SRC),
        ('tsx',        'demo.tsx', TSX_SRC),
    ]

    for lang, fname, src in cases:
        w = get_walker(lang)
        pf = w.parse_file(Path(fname), fname, src)
        print(f"  {lang}: {len(pf.classes)} classes, "
              f"{len(pf.functions)} functions, "
              f"{len(pf.imports)} imports, "
              f"{len(pf.parse_errors)} errors")
        if pf.parse_errors:
            for err in pf.parse_errors:
                print(f"      ERR: {err}")
""")
if not ok:
    sys.exit(1)

patch.finish()

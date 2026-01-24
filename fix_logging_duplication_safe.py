#!/usr/bin/env python3
"""
Safely removes logging.basicConfig blocks from ingest_sales_zip.py
without leaving dangling syntax.
"""

from pathlib import Path
import ast

TARGET = Path("/opt/mythos/sales_ingestion/ingest_sales_zip.py")

source = TARGET.read_text()
tree = ast.parse(source)

lines = source.splitlines()
remove_ranges = []

for node in tree.body:
    if (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and getattr(node.value.func, "attr", None) == "basicConfig"
    ):
        remove_ranges.append((node.lineno - 1, node.end_lineno))

# Remove from bottom to top so indices stay valid
for start, end in sorted(remove_ranges, reverse=True):
    for i in range(start, end):
        lines[i] = ""

TARGET.write_text("\n".join(lines))

print(f"Removed {len(remove_ranges)} logging.basicConfig block(s)")

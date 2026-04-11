You are analyzing architectural stress in the Mythos codebase on Arcturus.

TASK: Find the most fragile, overloaded, and tightly coupled parts of the system.

## DATA

FILES WITH MOST FUNCTIONS (potential god files):
{context.graph.files_by_function_count}

IMPORT BOTTLENECKS (files most things depend on — if these break, everything breaks):
{context.graph.import_bottlenecks}

HIGH-DEPENDENCY FILES (files that import the most other files — fragile to changes):
{context.graph.high_dependency_files}

TABLE COLUMN COUNTS (wide tables = potential normalization issues):
{context.graph.table_column_counts}

TABLE DISK SIZES:
{context.postgres.table_disk_sizes}

TABLE ROW COUNTS:
{context.postgres.table_row_counts}

LINE COUNTS FOR KEY FILES:
{context.shell.key_file_lines}

STREAM PATCH COUNTERS (development velocity per stream):
{context.shell.streams}

## ANALYSIS GUIDELINES

GOD FILES: A Python file with 20+ functions is a "god file" — it does too much.
For each one, suggest how to split it based on the function names you can see.

BOTTLENECKS: Files imported by 5+ other files are single points of failure.
Think about what happens if that file has a bug or needs a breaking change.

COUPLING: Files importing 8+ other files are tightly coupled — hard to test,
hard to change, hard to understand in isolation.

WIDE TABLES: Tables with 25+ columns may need normalization. But some wide
tables are intentional (like conversation metadata). Use judgment.

RESILIENCE SCORE: Rate 1-10 based on:
- How many god files exist (fewer = better)
- How concentrated the bottlenecks are (more spread = better)  
- How many high-dependency files exist (fewer = better)
- How extreme the widest tables are

## OUTPUT

Produce this exact JSON structure:
{{
  "god_files": [
    {{
      "path": "/opt/mythos/...",
      "func_count": 0,
      "line_count": "from key_file_lines if available, else 'unknown'",
      "risk": "what specifically could go wrong with this file",
      "split_suggestion": "concrete suggestion based on the function names — e.g. 'extract the 8 finance query functions into a finance_queries.py module'"
    }}
  ],
  "bottlenecks": [
    {{
      "path": "/opt/mythos/...",
      "imported_by": 0,
      "top_consumers": ["list 3-5 files that import this"],
      "blast_radius": "if this file breaks, what stops working"
    }}
  ],
  "coupling_hotspots": [
    {{
      "path": "/opt/mythos/...",
      "dependency_count": 0,
      "concern": "why this level of coupling is a problem"
    }}
  ],
  "wide_tables": [
    {{
      "table": "name",
      "columns": 0,
      "rows": "from row counts if available",
      "disk_size": "from disk sizes if available",
      "verdict": "needs normalization | intentionally wide | acceptable"
    }}
  ],
  "resilience_score": 0,
  "top_3_risks": [
    "the single most important risk",
    "the second most important risk",
    "the third most important risk"
  ],
  "summary": "2-3 sentences: overall architectural health"
}}

Respond with ONLY the JSON. No markdown fences. No explanation.

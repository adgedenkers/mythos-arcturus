You are writing the final archaeology report for the Mythos system on Arcturus.

You have two prior analysis reports. Combine them into a single prioritized report
with actionable recommendations.

## PRIOR ANALYSES

DEAD CODE ANALYSIS:
{phases.dead_code}

STRESS ANALYSIS:
{phases.stress}

## ADDITIONAL CONTEXT

SYSTEM STATS FROM GRAPH (use these exact numbers — do NOT make up your own):
{context.graph.system_stats}

DIRECTORY SIZES ON DISK:
{context.shell.dir_sizes}

PYTHON FILES MODIFIED SINCE ARCHITECTURE.MD WAS LAST UPDATED:
{context.shell.files_newer_than_docs} files have changed

STREAM STATUS:
{context.shell.streams}

## REPORT INSTRUCTIONS

Combine the dead code and stress analyses into a unified report. 

For each finding, assign:
- category: dead_code | fragility | complexity | data | documentation
- severity: critical (blocks development) | high (causes bugs) | medium (tech debt) | low (nice to fix)
- effort: small (<30 min) | medium (1-4 hours) | large (multi-session)

QUICK WINS must be genuinely achievable in under 30 minutes each.
Examples: delete a confirmed dead file, drop an empty unused table, add a missing __init__.py.

STRATEGIC RECOMMENDATIONS are bigger changes worth planning for.
Examples: split a god file, normalize a wide table, refactor a bottleneck.

BURIED TREASURES are non-obvious insights you noticed in the data.
Examples: an unexpected import chain, a file that's a hidden dependency hub,
a table with surprising row counts, a pattern in the code organization.

For the stats block, use the EXACT numbers from system_stats above.
Pull dead_file_candidates count from the dead code analysis.
Pull empty_tables count from the dead code analysis.
Pull god_files count from the stress analysis.
Pull resilience_score from the stress analysis.

## OUTPUT

Produce this exact JSON structure:
{{
  "report_title": "Mythos System Archaeology — {context.shell.streams}",
  "executive_summary": "3-4 sentences. Be specific — mention actual file names, table names, numbers.",
  "system_health_score": "1-10 integer",
  "findings": [
    {{
      "category": "dead_code|fragility|complexity|data|documentation",
      "severity": "critical|high|medium|low",
      "finding": "specific finding with file paths or table names",
      "recommendation": "specific actionable recommendation",
      "effort": "small|medium|large"
    }}
  ],
  "quick_wins": [
    "specific action that takes <30 min — include the exact file or table name"
  ],
  "strategic_recommendations": [
    "specific larger change — reference the actual code/tables involved"
  ],
  "buried_treasures": [
    "a non-obvious insight with specific details"
  ],
  "stats": {{
    "total_files": "from system_stats",
    "total_functions": "from system_stats",
    "total_tables": "from system_stats",
    "total_services": "from system_stats",
    "total_directories": "from system_stats",
    "dead_file_candidates": "from dead_code phase",
    "empty_tables": "from dead_code phase",
    "god_files": "from stress phase",
    "resilience_score": "from stress phase"
  }}
}}

CRITICAL: The stats block MUST use real numbers from the data provided above.
Do NOT estimate or round. Copy the exact values.

Respond with ONLY the JSON. No markdown fences. No explanation.

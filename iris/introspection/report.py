"""
Report generator - produces health report from introspection run.
"""
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("iris.introspection.report")


def generate_report(run_id, file_list, component_groups,
                    component_analyses=None, queue_tasks=0, neo4j_rels=0):
    """Generate a structured health report dict."""
    ca = component_analyses or {}
    total_lines = sum(f.get("line_count", 0) for f in file_list)
    total_size = sum(f.get("size_bytes", 0) for f in file_list)
    analyzed = sum(1 for f in file_list if f.get("llm_summary"))
    issues = []
    for f in file_list:
        for issue in f.get("llm_issues", []):
            issues.append({"file": f["file_path"], "issue": issue})

    components_detail = {}
    for comp, files in component_groups.items():
        comp_info = {
            "file_count": len(files),
            "total_lines": sum(f.get("line_count", 0) for f in files),
            "file_types": list(set(f.get("file_type", "?") for f in files)),
        }
        if comp in ca:
            comp_info["summary"] = ca[comp].get("component_summary", "")
            comp_info["health"] = ca[comp].get("health", "unknown")
            comp_info["doc_gaps"] = ca[comp].get("documentation_gaps", [])
        components_detail[comp] = comp_info

    report = {
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_files": len(file_list),
            "total_lines": total_lines,
            "total_size_bytes": total_size,
            "components": len(component_groups),
            "llm_analyzed": analyzed,
            "issues_found": len(issues),
            "queue_tasks_dispatched": queue_tasks,
            "neo4j_relationships": neo4j_rels,
        },
        "components": components_detail,
        "issues": issues[:50],  # Cap at 50 for readability
    }

    return report


def format_report_text(report):
    """Format report as human-readable text for CLI/Telegram output."""
    s = report.get("summary", {})
    lines = [
        "=== IRIS INTROSPECTION REPORT ===",
        f"Run: {report.get('run_id', 'unknown')}",
        f"Generated: {report.get('generated_at', 'unknown')}",
        "",
        f"Files scanned: {s.get('total_files', 0)}",
        f"Total lines: {s.get('total_lines', 0):,}",
        f"Components: {s.get('components', 0)}",
        f"LLM analyzed: {s.get('llm_analyzed', 0)}",
        f"Issues found: {s.get('issues_found', 0)}",
        f"Queue tasks: {s.get('queue_tasks_dispatched', 0)}",
        f"Neo4j rels: {s.get('neo4j_relationships', 0)}",
        "",
        "--- Components ---",
    ]

    for comp, detail in report.get("components", {}).items():
        health = detail.get("health", "")
        health_str = f" [{health}]" if health else ""
        lines.append(f"  {comp}: {detail.get('file_count', 0)} files, "
                     f"{detail.get('total_lines', 0):,} lines{health_str}")

    issues = report.get("issues", [])
    if issues:
        lines.append("")
        lines.append("--- Issues ---")
        for i in issues[:10]:
            lines.append(f"  {i.get('file', '?')}: {i.get('issue', '?')}")
        if len(issues) > 10:
            lines.append(f"  ... and {len(issues) - 10} more")

    return "\n".join(lines)

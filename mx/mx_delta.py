"""
mx_delta.py — Snapshot delta engine (SYS-0028)

Diffs two mx snapshots and classifies each change as:
  ✓ ADDITION   — something new appeared (table, file, etc.)
  ~ CHANGE     — something changed (service state, row count, git hash)
  ✗ REGRESSION — something broke (service went inactive, files missing, etc.)
  · NEUTRAL    — expected changes (git hash rotation after deploy)

Produces a human-readable delta report and a structured dict for journal/Iris.
"""

from dataclasses import dataclass, field
from typing import Literal

ChangeType = Literal["ADDITION", "CHANGE", "REGRESSION", "NEUTRAL"]

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


@dataclass
class DeltaEntry:
    category: str          # "services", "git", "postgres", "integrity"
    key: str               # what changed
    before: str
    after: str
    change_type: ChangeType
    message: str


@dataclass
class DeltaReport:
    entries: list[DeltaEntry] = field(default_factory=list)
    regressions: list[str] = field(default_factory=list)
    has_regressions: bool = False

    def add(self, entry: DeltaEntry):
        self.entries.append(entry)
        if entry.change_type == "REGRESSION":
            self.regressions.append(entry.message)
            self.has_regressions = True

    def summary_line(self) -> str:
        additions = sum(1 for e in self.entries if e.change_type == "ADDITION")
        changes = sum(1 for e in self.entries if e.change_type == "CHANGE")
        regressions = len(self.regressions)
        neutrals = sum(1 for e in self.entries if e.change_type == "NEUTRAL")
        parts = []
        if additions:
            parts.append(f"+{additions} added")
        if changes:
            parts.append(f"~{changes} changed")
        if regressions:
            parts.append(f"✗{regressions} regression{'s' if regressions != 1 else ''}")
        if neutrals:
            parts.append(f"·{neutrals} neutral")
        return "  |  ".join(parts) if parts else "no changes detected"

    def to_dict(self) -> dict:
        return {
            "has_regressions": self.has_regressions,
            "regressions": self.regressions,
            "summary": self.summary_line(),
            "entries": [
                {
                    "category": e.category,
                    "key": e.key,
                    "before": e.before,
                    "after": e.after,
                    "change_type": e.change_type,
                    "message": e.message,
                }
                for e in self.entries
            ],
        }


def diff_snapshots(before: dict, after: dict) -> DeltaReport:
    """
    Compare two snapshots and produce a DeltaReport.
    """
    report = DeltaReport()

    # ── Services ─────────────────────────────────────────────────────────────
    svc_before = before.get("services", {})
    svc_after = after.get("services", {})

    for svc, state_after in svc_after.items():
        state_before = svc_before.get(svc)
        if state_before is None:
            report.add(DeltaEntry(
                category="services", key=svc,
                before="(new)", after=state_after,
                change_type="ADDITION",
                message=f"New service: {svc} ({state_after})",
            ))
        elif state_before != state_after:
            if state_after == "inactive":
                report.add(DeltaEntry(
                    category="services", key=svc,
                    before=state_before, after=state_after,
                    change_type="REGRESSION",
                    message=f"{svc}: active → FAILED/inactive",
                ))
            else:
                report.add(DeltaEntry(
                    category="services", key=svc,
                    before=state_before, after=state_after,
                    change_type="CHANGE",
                    message=f"{svc}: {state_before} → {state_after}",
                ))

    for svc in svc_before:
        if svc not in svc_after:
            report.add(DeltaEntry(
                category="services", key=svc,
                before=svc_before[svc], after="(gone)",
                change_type="REGRESSION",
                message=f"{svc}: disappeared from service list",
            ))

    # ── Git ───────────────────────────────────────────────────────────────────
    git_before = before.get("git", {})
    git_after = after.get("git", {})

    if git_before.get("hash") != git_after.get("hash"):
        # A new commit is expected after a deploy — neutral unless we regressed
        report.add(DeltaEntry(
            category="git", key="commit",
            before=git_before.get("hash", "?"),
            after=git_after.get("hash", "?"),
            change_type="NEUTRAL",
            message=f"Git: {git_before.get('hash','?')} → {git_after.get('hash','?')} · {git_after.get('message','')}",
        ))

    if not git_before.get("clean", True) and git_after.get("clean", True):
        report.add(DeltaEntry(
            category="git", key="clean",
            before="dirty", after="clean",
            change_type="NEUTRAL",
            message="Git: working tree is now clean",
        ))
    elif git_before.get("clean", True) and not git_after.get("clean", True):
        report.add(DeltaEntry(
            category="git", key="clean",
            before="clean", after="dirty",
            change_type="CHANGE",
            message="Git: working tree now has uncommitted changes",
        ))

    # ── PostgreSQL ────────────────────────────────────────────────────────────
    pg_before = before.get("postgres", {})
    pg_after = after.get("postgres", {})

    tc_before = pg_before.get("table_count", 0)
    tc_after = pg_after.get("table_count", 0)
    if tc_before != tc_after:
        diff = tc_after - tc_before
        report.add(DeltaEntry(
            category="postgres", key="table_count",
            before=str(tc_before), after=str(tc_after),
            change_type="ADDITION" if diff > 0 else "REGRESSION",
            message=f"Tables: {tc_before} → {tc_after} ({'+' if diff > 0 else ''}{diff})",
        ))

    # Row count regressions (significant drops = likely data loss)
    rc_before = pg_before.get("row_counts", {})
    rc_after = pg_after.get("row_counts", {})
    for table, count_after in rc_after.items():
        count_before = rc_before.get(table, count_after)
        if count_before > 0 and count_after < count_before:
            drop_pct = (count_before - count_after) / count_before * 100
            if drop_pct > 10:  # only flag significant drops
                report.add(DeltaEntry(
                    category="postgres", key=f"rows.{table}",
                    before=str(count_before), after=str(count_after),
                    change_type="REGRESSION",
                    message=f"Row count drop: {table} {count_before} → {count_after} ({drop_pct:.0f}% loss)",
                ))

    # ── Integrity ─────────────────────────────────────────────────────────────
    integ_before = before.get("integrity", {})
    integ_after = after.get("integrity", {})

    if integ_before.get("available") and integ_after.get("available"):
        # Files missing
        missing_before = integ_before.get("files_missing", 0)
        missing_after = integ_after.get("files_missing", 0)
        if missing_after > missing_before:
            report.add(DeltaEntry(
                category="integrity", key="files_missing",
                before=str(missing_before), after=str(missing_after),
                change_type="REGRESSION",
                message=f"Files missing: {missing_before} → {missing_after} (+{missing_after - missing_before})",
            ))
        elif missing_after < missing_before:
            report.add(DeltaEntry(
                category="integrity", key="files_missing",
                before=str(missing_before), after=str(missing_after),
                change_type="NEUTRAL",
                message=f"Files missing resolved: {missing_before} → {missing_after}",
            ))

        # Services unhealthy
        unhealthy_before = integ_before.get("services_unhealthy", 0)
        unhealthy_after = integ_after.get("services_unhealthy", 0)
        if unhealthy_after > unhealthy_before:
            report.add(DeltaEntry(
                category="integrity", key="services_unhealthy",
                before=str(unhealthy_before), after=str(unhealthy_after),
                change_type="REGRESSION",
                message=f"Unhealthy services: {unhealthy_before} → {unhealthy_after}",
            ))

    return report


def print_delta_report(report: DeltaReport, pre_label: str = "pre", post_label: str = "post"):
    """Print a formatted delta report to the terminal."""
    print(f"\n{BOLD}── Delta Report ({pre_label} → {post_label}) ─────────────────────────{RESET}")

    if not report.entries:
        print(f"  {DIM}No changes detected.{RESET}")
    else:
        for entry in report.entries:
            if entry.change_type == "REGRESSION":
                icon = f"{RED}✗{RESET}"
            elif entry.change_type == "ADDITION":
                icon = f"{GREEN}+{RESET}"
            elif entry.change_type == "NEUTRAL":
                icon = f"{DIM}·{RESET}"
            else:
                icon = f"{YELLOW}~{RESET}"
            print(f"  {icon} {entry.message}")

    print(f"{DIM}{'─' * 55}{RESET}")
    print(f"  {report.summary_line()}")

    if report.has_regressions:
        print(f"\n  {RED}{BOLD}⚠  Regressions detected.{RESET}")
    else:
        print(f"\n  {GREEN}✓ System healthy.{RESET}")
    print()

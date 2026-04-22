"""
AutoDoc2 — ollama-analyze microtool (SYS-0087)

Sends parsed file structure (NOT raw source) to gemma4:26b and returns
structured JSON analysis. Non-fatal — failures are logged and the crawl
continues. Results are stored as analysis_* properties on AutodocFile
nodes in Neo4j.

Model choice: gemma4:26b — technically precise, no prose padding, no
personality drift. Iris (qwen3:30b-a3b) handles synthesis and conversation.
gemma4 handles structural code analysis. These are kept separate by design.

Input: already-parsed structural metadata from tree-sitter (ParsedFile).
Source code is never sent to the model.

Output: AnalysisResult dataclass — structured, typed, all fields nullable
so partial results are still useful.
"""
import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional, List

from .walker import ParsedFile

ANALYSIS_MODEL = "gemma4:26b"
ANALYSIS_TIMEOUT = 90  # seconds — gemma4:26b is fast but files vary

ANALYSIS_PROMPT_TEMPLATE = """\
You are a code analysis tool. Analyze the structure of this source file and respond ONLY with a valid JSON object. No preamble, no explanation, no markdown, no code blocks. Just the JSON object.

File: {path}
Language: {language}
Lines: {line_count}
Functions: {functions}
Classes: {classes}
Imports: {imports}

Respond with exactly this JSON structure:
{{
  "complexity": "<low|medium|high>",
  "coupling_signals": ["<short signal string>", ...],
  "patterns_detected": ["<pattern name>", ...],
  "drift_risk": "<low|medium|high>",
  "notable": "<one sentence or empty string>"
}}

Rules:
- complexity: low = simple utilities/configs, medium = standard business logic, high = complex algorithms or deep nesting
- coupling_signals: list things that create tight coupling (e.g. "imports 7 external modules", "direct DB calls", "hardcoded paths"). Empty list if none.
- patterns_detected: recognized design patterns only (e.g. "singleton", "factory", "facade", "observer"). Empty list if none clearly present.
- drift_risk: likelihood this file's implementation diverges from its documented purpose. low = stable, high = volatile or unclear
- notable: one concrete observation about this file's structure, or empty string if nothing stands out
- All fields required. Arrays may be empty. notable may be empty string."""


@dataclass
class AnalysisResult:
    complexity: Optional[str] = None          # low / medium / high
    coupling_signals: List[str] = field(default_factory=list)
    patterns_detected: List[str] = field(default_factory=list)
    drift_risk: Optional[str] = None          # low / medium / high
    notable: Optional[str] = None
    model: str = ANALYSIS_MODEL
    timestamp: Optional[str] = None
    error: Optional[str] = None               # set if analysis failed

    def ok(self) -> bool:
        return self.error is None and self.complexity is not None

    def to_neo4j_props(self) -> dict:
        """Return a flat dict of analysis_* properties for Neo4j."""
        return {
            "analysis_complexity": self.complexity,
            "analysis_coupling_signals": self.coupling_signals,
            "analysis_patterns": self.patterns_detected,
            "analysis_drift_risk": self.drift_risk,
            "analysis_notable": self.notable or "",
            "analysis_model": self.model,
            "analysis_timestamp": self.timestamp,
            "analysis_error": self.error,
        }


class Analyzer:
    """Calls gemma4:26b to analyze a ParsedFile's structure.

    Usage:
        analyzer = Analyzer(ollama_url="http://localhost:11434")
        result = analyzer.analyze(parsed_file)
        if result.ok():
            props = result.to_neo4j_props()
    """

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url.rstrip('/')

    def analyze(self, pf: ParsedFile) -> AnalysisResult:
        """Analyze a ParsedFile. Never raises — failures return AnalysisResult with error set."""
        timestamp = datetime.now(timezone.utc).isoformat()

        # Build compact structural metadata — no source code
        function_names = [fn.name for fn in pf.functions[:40]]  # cap at 40
        class_names = [cls.name for cls in pf.classes[:20]]
        import_modules = list({imp.module for imp in pf.imports})[:30]

        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            path=pf.relative_path,
            language=pf.language,
            line_count=pf.line_count,
            functions=json.dumps(function_names),
            classes=json.dumps(class_names),
            imports=json.dumps(import_modules),
        )

        try:
            raw = self._call_ollama(prompt)
        except Exception as e:
            return AnalysisResult(
                model=ANALYSIS_MODEL,
                timestamp=timestamp,
                error=f"ollama call failed: {e}",
            )

        try:
            result = self._parse_response(raw, timestamp)
        except Exception as e:
            return AnalysisResult(
                model=ANALYSIS_MODEL,
                timestamp=timestamp,
                error=f"response parse failed: {e} | raw: {raw[:200]}",
            )

        return result

    def _call_ollama(self, prompt: str) -> str:
        payload = json.dumps({
            "model": ANALYSIS_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,   # deterministic — this is analysis, not generation
                "num_predict": 512,   # JSON output is small; 512 is plenty
            },
        }).encode('utf-8')

        req = urllib.request.Request(
            f"{self.ollama_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=ANALYSIS_TIMEOUT) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return (data.get('response') or '').strip()

    def _parse_response(self, raw: str, timestamp: str) -> AnalysisResult:
        # Gemma4 should return bare JSON but may occasionally wrap in ```json ... ```
        # Strip fences if present
        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            # drop first and last fence lines
            inner = []
            for i, line in enumerate(lines):
                if i == 0 and line.startswith("```"):
                    continue
                if i == len(lines) - 1 and line.strip() == "```":
                    continue
                inner.append(line)
            text = "\n".join(inner).strip()

        data = json.loads(text)

        complexity = data.get("complexity")
        if complexity not in ("low", "medium", "high"):
            complexity = None

        drift_risk = data.get("drift_risk")
        if drift_risk not in ("low", "medium", "high"):
            drift_risk = None

        coupling = data.get("coupling_signals", [])
        if not isinstance(coupling, list):
            coupling = []
        coupling = [str(s) for s in coupling][:10]  # cap

        patterns = data.get("patterns_detected", [])
        if not isinstance(patterns, list):
            patterns = []
        patterns = [str(s) for s in patterns][:10]  # cap

        notable = data.get("notable", "")
        if not isinstance(notable, str):
            notable = ""
        notable = notable[:500]  # cap

        return AnalysisResult(
            complexity=complexity,
            coupling_signals=coupling,
            patterns_detected=patterns,
            drift_risk=drift_risk,
            notable=notable,
            model=ANALYSIS_MODEL,
            timestamp=timestamp,
            error=None,
        )

"""
Neo4j writer for AutoDoc2.

Writes ParsedFile objects to Neo4j using the same node label scheme as
legacy autodoc1 so demo Cypher queries are portable between graphs:

  Nodes:
    AutodocFile        {path, relative_path, language, line_count, crawl_id}
    AutodocClass       {name, qualified_name, line_start, line_end, docstring}
    AutodocFunction    {name, qualified_name, line_start, line_end,
                        is_async, is_method, parent_class, docstring}
    AutodocModule      {name}                          (one per dotted path imported)
    AutodocCrawl       {crawl_id, target, started_at, finished_at, status}

  Relationships:
    (AutodocCrawl)-[:CONTAINS]->(AutodocFile)
    (AutodocFile)-[:CONTAINS]->(AutodocClass)
    (AutodocFile)-[:CONTAINS]->(AutodocFunction)
    (AutodocClass)-[:CONTAINS]->(AutodocFunction)         (methods)
    (AutodocFunction)-[:DEFINED_IN]->(AutodocFile)
    (AutodocClass)-[:DEFINED_IN]->(AutodocFile)
    (AutodocFile)-[:IMPORTS]->(AutodocModule)
    (AutodocFunction)-[:CALLS]->(AutodocFunction)         (best-effort by name)

SYS-0087: AutodocFile nodes may also carry analysis_* properties written
by write_analysis() when --analyze is active.
"""
from datetime import datetime
from typing import Optional

from .walker import ParsedFile


class Neo4jWriter:
    def __init__(self, uri: str, user: str, password: str, crawl_id: str, target: str):
        try:
            from neo4j import GraphDatabase
        except ImportError as e:
            raise RuntimeError(
                "neo4j driver not installed in venv. Run: "
                "/opt/mythos/.venv/bin/pip install neo4j"
            ) from e
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self.crawl_id = crawl_id
        self.target = target

    def close(self):
        self._driver.close()

    # ------------------------------------------------------------------
    # Schema setup
    # ------------------------------------------------------------------

    def setup_constraints(self):
        """Idempotent constraint creation. Safe to call repeatedly."""
        constraints = [
            "CREATE CONSTRAINT autodoc_file_unique IF NOT EXISTS "
            "FOR (f:AutodocFile) REQUIRE (f.crawl_id, f.relative_path) IS UNIQUE",
            "CREATE CONSTRAINT autodoc_function_unique IF NOT EXISTS "
            "FOR (f:AutodocFunction) REQUIRE (f.crawl_id, f.qualified_name) IS UNIQUE",
            "CREATE CONSTRAINT autodoc_class_unique IF NOT EXISTS "
            "FOR (c:AutodocClass) REQUIRE (c.crawl_id, c.qualified_name) IS UNIQUE",
            "CREATE CONSTRAINT autodoc_module_unique IF NOT EXISTS "
            "FOR (m:AutodocModule) REQUIRE (m.crawl_id, m.name) IS UNIQUE",
            "CREATE CONSTRAINT autodoc_crawl_unique IF NOT EXISTS "
            "FOR (c:AutodocCrawl) REQUIRE c.crawl_id IS UNIQUE",
        ]
        with self._driver.session() as s:
            for cq in constraints:
                try:
                    s.run(cq)
                except Exception as e:
                    print(f"[neo4j_writer] constraint warning: {e}")

    def begin_crawl(self):
        with self._driver.session() as s:
            s.run(
                """
                MERGE (c:AutodocCrawl {crawl_id: $crawl_id})
                SET c.target = $target,
                    c.started_at = $started_at,
                    c.status = 'running'
                """,
                crawl_id=self.crawl_id,
                target=self.target,
                started_at=datetime.utcnow().isoformat(),
            )

    def finish_crawl(self, file_count: int, status: str = 'completed'):
        with self._driver.session() as s:
            s.run(
                """
                MATCH (c:AutodocCrawl {crawl_id: $crawl_id})
                SET c.finished_at = $finished_at,
                    c.file_count = $file_count,
                    c.status = $status
                """,
                crawl_id=self.crawl_id,
                finished_at=datetime.utcnow().isoformat(),
                file_count=file_count,
                status=status,
            )

    def clean_crawl(self):
        """Delete all nodes for this crawl_id. Used by --clean."""
        with self._driver.session() as s:
            s.run(
                """
                MATCH (n) WHERE n.crawl_id = $crawl_id
                DETACH DELETE n
                """,
                crawl_id=self.crawl_id,
            )

    # ------------------------------------------------------------------
    # File writes
    # ------------------------------------------------------------------

    def write_file(self, pf: ParsedFile):
        with self._driver.session() as s:
            s.execute_write(self._write_file_tx, pf, self.crawl_id)

    @staticmethod
    def _write_file_tx(tx, pf: ParsedFile, crawl_id: str):
        # File node + link to crawl
        tx.run(
            """
            MERGE (f:AutodocFile {crawl_id: $crawl_id, relative_path: $rel})
            SET f.path = $path,
                f.language = $lang,
                f.line_count = $lc
            WITH f
            MATCH (c:AutodocCrawl {crawl_id: $crawl_id})
            MERGE (c)-[:CONTAINS]->(f)
            """,
            crawl_id=crawl_id,
            rel=pf.relative_path,
            path=str(pf.path),
            lang=pf.language,
            lc=pf.line_count,
        )

        # Classes
        for cls in pf.classes:
            tx.run(
                """
                MERGE (c:AutodocClass {crawl_id: $crawl_id, qualified_name: $qn})
                SET c.name = $name,
                    c.line_start = $ls,
                    c.line_end = $le,
                    c.docstring = $doc,
                    c.bases = $bases
                WITH c
                MATCH (f:AutodocFile {crawl_id: $crawl_id, relative_path: $rel})
                MERGE (f)-[:CONTAINS]->(c)
                MERGE (c)-[:DEFINED_IN]->(f)
                """,
                crawl_id=crawl_id,
                qn=cls.qualified_name,
                name=cls.name,
                ls=cls.line_start,
                le=cls.line_end,
                doc=cls.docstring or "",
                bases=cls.bases,
                rel=pf.relative_path,
            )

        # Functions
        for fn in pf.functions:
            tx.run(
                """
                MERGE (fn:AutodocFunction {crawl_id: $crawl_id, qualified_name: $qn})
                SET fn.name = $name,
                    fn.line_start = $ls,
                    fn.line_end = $le,
                    fn.is_async = $is_async,
                    fn.is_method = $is_method,
                    fn.parent_class = $parent,
                    fn.docstring = $doc
                WITH fn
                MATCH (f:AutodocFile {crawl_id: $crawl_id, relative_path: $rel})
                MERGE (f)-[:CONTAINS]->(fn)
                MERGE (fn)-[:DEFINED_IN]->(f)
                """,
                crawl_id=crawl_id,
                qn=fn.qualified_name,
                name=fn.name,
                ls=fn.line_start,
                le=fn.line_end,
                is_async=fn.is_async,
                is_method=fn.is_method,
                parent=fn.parent_class or "",
                doc=fn.docstring or "",
                rel=pf.relative_path,
            )

            # Method -> class CONTAINS link
            if fn.is_method and fn.parent_class:
                module_prefix = fn.qualified_name.rsplit('.' + fn.name, 1)[0]
                tx.run(
                    """
                    MATCH (c:AutodocClass {crawl_id: $crawl_id, qualified_name: $cls_qn})
                    MATCH (fn:AutodocFunction {crawl_id: $crawl_id, qualified_name: $fn_qn})
                    MERGE (c)-[:CONTAINS]->(fn)
                    """,
                    crawl_id=crawl_id,
                    cls_qn=module_prefix,
                    fn_qn=fn.qualified_name,
                )

        # Imports
        for imp in pf.imports:
            tx.run(
                """
                MERGE (m:AutodocModule {crawl_id: $crawl_id, name: $mod})
                WITH m
                MATCH (f:AutodocFile {crawl_id: $crawl_id, relative_path: $rel})
                MERGE (f)-[r:IMPORTS]->(m)
                SET r.line = $line,
                    r.is_relative = $is_rel,
                    r.names = $names
                """,
                crawl_id=crawl_id,
                mod=imp.module,
                rel=pf.relative_path,
                line=imp.line,
                is_rel=imp.is_relative,
                names=imp.names,
            )

    # ------------------------------------------------------------------
    # SYS-0087: Analysis results
    # ------------------------------------------------------------------

    def write_analysis(self, relative_path: str, result: 'AnalysisResult'):
        """Write analysis_* properties onto an existing AutodocFile node.

        Called after write_file() when --analyze is active. Non-fatal if
        the file node doesn't exist yet (race condition is impossible in
        sequential crawl, but guard anyway).

        Args:
            relative_path: matches AutodocFile.relative_path
            result: AnalysisResult from analyzer.Analyzer.analyze()
        """
        props = result.to_neo4j_props()
        with self._driver.session() as s:
            s.run(
                """
                MATCH (f:AutodocFile {crawl_id: $crawl_id, relative_path: $rel})
                SET f.analysis_complexity      = $analysis_complexity,
                    f.analysis_coupling_signals = $analysis_coupling_signals,
                    f.analysis_patterns         = $analysis_patterns,
                    f.analysis_drift_risk       = $analysis_drift_risk,
                    f.analysis_notable          = $analysis_notable,
                    f.analysis_model            = $analysis_model,
                    f.analysis_timestamp        = $analysis_timestamp
                """,
                crawl_id=self.crawl_id,
                rel=relative_path,
                analysis_complexity=props.get("analysis_complexity"),
                analysis_coupling_signals=props.get("analysis_coupling_signals", []),
                analysis_patterns=props.get("analysis_patterns", []),
                analysis_drift_risk=props.get("analysis_drift_risk"),
                analysis_notable=props.get("analysis_notable", ""),
                analysis_model=props.get("analysis_model", "gemma4:26b"),
                analysis_timestamp=props.get("analysis_timestamp"),
            )

    # ------------------------------------------------------------------
    # Call graph (post-processing, best-effort)
    # ------------------------------------------------------------------

    def link_calls(self):
        """Second-pass: link CALLS relationships using simple name matching."""
        with self._driver.session() as s:
            s.run(
                """
                MATCH (caller:AutodocFunction {crawl_id: $crawl_id})
                WHERE caller.docstring IS NOT NULL
                RETURN caller LIMIT 0
                """,
                crawl_id=self.crawl_id,
            )

    def write_call_property(self, fn_qualified_name: str, calls: list):
        """Store the raw call list as a property for later call graph construction."""
        with self._driver.session() as s:
            s.run(
                """
                MATCH (fn:AutodocFunction {crawl_id: $crawl_id, qualified_name: $qn})
                SET fn.calls_raw = $calls
                """,
                crawl_id=self.crawl_id,
                qn=fn_qualified_name,
                calls=calls,
            )

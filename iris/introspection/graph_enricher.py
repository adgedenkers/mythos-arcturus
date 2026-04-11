"""
Graph Enricher - Neo4j nodes and relationships from introspection.
"""
import logging

logger = logging.getLogger("iris.introspection.graph_enricher")


def enrich_graph(driver, run_id, file_list, component_groups):
    """Update Neo4j with SystemComponent, SystemFile nodes and relationships."""
    if driver is None:
        logger.warning("No Neo4j driver, skipping graph enrichment")
        return 0

    count = 0
    with driver.session() as s:
        s.run("MERGE (r:IntrospectionRun {run_id: $rid}) SET r.updated_at = datetime()", rid=run_id)

        for cname, cfiles in component_groups.items():
            s.run("MERGE (c:SystemComponent {name: $n}) SET c.file_count = $cnt, c.updated_at = datetime()",
                  n=cname, cnt=len(cfiles))

        for f in file_list:
            props = {
                "path": f["file_path"],
                "component": f.get("component", "root"),
                "file_type": f.get("file_type", "unknown"),
                "line_count": f.get("line_count", 0),
                "content_hash": f.get("content_hash", ""),
                "llm_purpose": f.get("llm_purpose", ""),
            }
            s.run("MERGE (sf:SystemFile {path: $p}) SET sf += $props, sf.updated_at = datetime()",
                  p=f["file_path"], props=props)

            s.run("MATCH (c:SystemComponent {name: $c}) MATCH (sf:SystemFile {path: $p}) MERGE (c)-[:CONTAINS]->(sf)",
                  c=f.get("component", "root"), p=f["file_path"])
            count += 1

            s.run("MATCH (r:IntrospectionRun {run_id: $rid}) MATCH (sf:SystemFile {path: $p}) MERGE (r)-[:SCANNED]->(sf)",
                  rid=run_id, p=f["file_path"])
            count += 1

            for dep in f.get("llm_dependencies", []):
                s.run("MATCH (sf:SystemFile {path: $p}) MERGE (d:SystemDependency {name: $dn}) MERGE (sf)-[:DEPENDS_ON]->(d)",
                      p=f["file_path"], dn=dep)
                count += 1

    logger.info(f"Neo4j enrichment: {count} relationships")
    return count

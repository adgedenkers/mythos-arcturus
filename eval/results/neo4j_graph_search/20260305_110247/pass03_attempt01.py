import os
import logging
import re
from dotenv import load_dotenv
from engine.base import SkillBase, SkillRequest, SkillResponse
from neo4j import GraphDatabase

load_dotenv('/opt/mythos/.env')

def _get_driver():
    return GraphDatabase.driver(
        os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        auth=(os.getenv('NEO4J_USER', 'neo4j'), os.getenv('NEO4J_PASSWORD', ''))
    )

class Neo4jGraphSearchSkill(SkillBase):
    name = 'neo4j_graph_search'
    triggers = [
        'ontology', 'graph', 'soul', 'souls', 'lineage', 
        'spiritual concept', 'term', 'definition', 
        'what does mean', 'define'
    ]
    cache_ttl = 600

    async def execute(self, request: SkillRequest) -> SkillResponse:
        query = request.message
        search_term = self._extract_search_term(query)
        
        if not search_term:
            return SkillResponse(
                response="I couldn't extract a meaningful search term from your query.",
                success=False
            )
        
        # First try to search in ontology terms
        ontology_results = self._search_ontology(search_term)
        
        # If no ontology results, search in nodes
        if not ontology_results:
            node_results = self._search_nodes(search_term)
            if not node_results:
                return SkillResponse(
                    response=f"No results found for '{search_term}'.",
                    success=False
                )
            else:
                summary = self._build_summary(node_results)
                return SkillResponse(
                    response=summary,
                    success=True
                )
        else:
            summary = self._build_summary(ontology_results)
            return SkillResponse(
                response=summary,
                success=True
            )

    def _extract_search_term(self, query: str) -> str:
        # Convert to lowercase
        query = query.lower()
        
        # Remove triggers
        triggers_to_remove = [
            'spiritual concept', 'what does mean', 'ontology', 'define', 
            'definition', 'graph', 'lineage', 'search for', 'search', 
            'find', 'about', 'what', 'the'
        ]
        
        for trigger in triggers_to_remove:
            query = query.replace(trigger, '')
        
        # Normalize whitespace
        query = re.sub(r'\s+', ' ', query)
        
        # Remove leading/trailing whitespace
        query = query.strip()
        
        # Remove single-character words
        words = query.split()
        filtered_words = [word for word in words if len(word) > 1]
        query = ' '.join(filtered_words)
        
        return query if len(query) >= 2 else ""

    def _search_ontology(self, term: str) -> list:
        driver = _get_driver()
        try:
            with driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:OntologyTerm)
                    WHERE toLower(t.name) CONTAINS toLower($term)
                    RETURN t.name as name, t.definition as definition, t.category as category
                    LIMIT 10
                    """,
                    term=term
                )
                records = list(result)
                return [
                    {
                        'name': record['name'],
                        'definition': record['definition'],
                        'category': record['category']
                    }
                    for record in records
                ]
        finally:
            driver.close()

    def _search_nodes(self, term: str) -> list:
        driver = _get_driver()
        try:
            with driver.session() as session:
                result = session.run(
                    """
                    MATCH (n)
                    WHERE n.name CONTAINS $term
                    RETURN n.name AS name, labels(n) AS labels
                    LIMIT 10
                    """,
                    term=term
                )
                records = list(result)
                return [
                    {
                        'name': record['name'],
                        'labels': record['labels']
                    }
                    for record in records
                ]
        finally:
            driver.close()

    def _build_summary(self, results: list) -> str:
        if not results:
            return "No results found."
        
        summary_parts = []
        for result in results:
            if 'name' in result and 'definition' in result:
                summary_parts.append(f"**{result['name']}**: {result['definition']}")
            elif 'name' in result:
                summary_parts.append(f"**{result['name']}**")
        
        return "\n\n".join(summary_parts)
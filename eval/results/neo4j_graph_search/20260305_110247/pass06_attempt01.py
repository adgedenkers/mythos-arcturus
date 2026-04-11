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
        term = self._extract_search_term(query)
        
        if not term:
            return SkillResponse(
                response="Search the knowledge graph by providing a term or concept.",
                success=False
            )
        
        ontology_results = []
        node_results = []
        
        try:
            ontology_results = self._search_ontology(term)
            node_results = self._search_nodes(term)
        except Exception as e:
            logging.error(f"Error during Neo4j search: {e}")
            return SkillResponse(
                response=f"An error occurred while searching: {str(e)}",
                success=False
            )
        finally:
            pass  # Driver management handled in individual search methods
        
        summary_parts = []
        
        if ontology_results:
            summary_parts.append(f"Found {len(ontology_results)} ontology term(s):")
            for result in ontology_results:
                category = f" ({result['category']})" if result.get('category') else ""
                summary_parts.append(f"  {result['name']}{category} - {result['definition']}")
        
        if node_results:
            summary_parts.append(f"Found {len(node_results)} graph node(s):")
            for result in node_results:
                summary_parts.append(f"  {result['type']}: {result['name']}")
        
        if not ontology_results and not node_results:
            summary = f"No results found for '{term}'."
        else:
            summary = "\n".join(summary_parts)
        
        return SkillResponse(
            skill_name=self.name,
            data={'ontology': ontology_results, 'nodes': node_results, 'search_term': term},
            response=summary,
            success=True,
            confidence=0.9,
            sources=['neo4j']
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
        
        # Remove non-ASCII characters
        query = re.sub(r'[^\x00-\x7f]', '', query)
        
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
                    WHERE any(label IN labels(n) WHERE label IN ['Person', 'Soul', 'SpiritualConcept'])
                    AND toLower(n.name) CONTAINS toLower($term)
                    RETURN labels(n) as labels, n.name as name, n.canonical_id as canonical_id
                    LIMIT 10
                    """,
                    term=term
                )
                records = list(result)
                return [
                    {
                        'type': record['labels'][0],
                        'name': record['name'],
                        'canonical_id': record['canonical_id']
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
        
        return "\n\n".join(summary_parts) if summary_parts else "No results found."
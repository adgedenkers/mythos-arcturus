import os
import logging
from dotenv import load_dotenv
from engine.base import SkillBase, SkillRequest, SkillResponse
from neo4j import GraphDatabase

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

def _get_driver():
    return GraphDatabase.driver(
        os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        auth=(os.getenv('NEO4J_USER', 'neo4j'), os.getenv('NEO4J_PASSWORD', ''))
    )

class Neo4jGraphSearchSkill(SkillBase):
    name = 'neo4j_graph_search'
    triggers = ['ontology', 'graph', 'soul', 'souls', 'lineage', 'spiritual concept', 'term', 'definition', 'what does mean', 'define']
    cache_ttl = 600

    async def execute(self, request: SkillRequest) -> SkillResponse:
        pass

    def _extract_search_term(self, request: SkillRequest) -> str:
        message = request.message.lower()
        triggers_to_remove = ['spiritual concept', 'what does mean', 'ontology', 'define', 'definition', 'graph', 'lineage', 'search for', 'search', 'find', 'about', 'what', 'the']
        for trigger in triggers_to_remove:
            message = message.replace(trigger, '')
        message = ' '.join(message.split())
        words = message.split()
        filtered_words = [word for word in words if len(word) > 1]
        term = ' '.join(filtered_words)
        if len(term) >= 2:
            return term
        else:
            return None

    def _search_ontology(self, term: str) -> list:
        driver = _get_driver()
        results = []
        try:
            with driver.session() as session:
                query = "MATCH (t:OntologyTerm) WHERE toLower(t.name) CONTAINS toLower($term) RETURN t.name as name, t.definition as definition, t.category as category LIMIT 10"
                result = session.run(query, term=term)
                records = list(result)
                for record in records:
                    results.append({
                        'name': record['name'],
                        'definition': record['definition'],
                        'category': record['category']
                    })
        finally:
            driver.close()
        return results

    def _search_nodes(self, term: str) -> list:
        pass

    def _build_summary(self, results: list) -> str:
        pass
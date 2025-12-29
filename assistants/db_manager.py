#!/usr/bin/env python3

import os
import sys
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase
import psycopg2
from ollama import Client

# Load environment variables
load_dotenv()

class MythosManager:
    def __init__(self):
        # Neo4j connection
        self.neo4j_driver = GraphDatabase.driver(
            os.getenv('NEO4J_URI'),
            auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
        )
        
        # PostgreSQL connection
        self.pg_conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
        
        # Ollama client
        self.ollama = Client(host=os.getenv('OLLAMA_HOST'))
        self.model = os.getenv('OLLAMA_MODEL')
    
    def route_query(self, natural_language_query):
        """Determine which database to use based on query content"""
        
        # Keywords that strongly indicate PostgreSQL
        postgres_keywords = ['table', 'column', 'row', 'schema', 'index', 'view', 'sequence']
        
        # Check for explicit PostgreSQL indicators
        query_lower = natural_language_query.lower()
        if any(keyword in query_lower for keyword in postgres_keywords):
            return 'postgres'
        
        # Keywords that strongly indicate Neo4j
        neo4j_keywords = ['node', 'relationship', 'graph', 'path', 'lineage', 'connection', 'entity']
        if any(keyword in query_lower for keyword in neo4j_keywords):
            return 'neo4j'
        
        # If ambiguous, ask Ollama
        prompt = f"""You are a database router. Determine if this query should go to:
- NEO4J (for graph relationships, lineages, connections, entities, nodes, paths)
- POSTGRES (for structured tables, columns, rows, schemas, SQL operations)

Query: {natural_language_query}

Respond with ONLY one word: NEO4J or POSTGRES"""

        response = self.ollama.generate(model=self.model, prompt=prompt)
        decision = response['response'].strip().upper()
        
        if 'POSTGRES' in decision:
            return 'postgres'
        else:
            return 'neo4j'  # Default to Neo4j for entity/relationship queries


    def generate_cypher(self, natural_language_query):
        """Generate Cypher query from natural language"""
        
        prompt = f"""You are a Neo4j Cypher expert. Convert this natural language query into a valid Cypher query.

Query: {natural_language_query}

Respond with ONLY the Cypher query, no explanations. Use proper Cypher syntax."""

        response = self.ollama.generate(model=self.model, prompt=prompt)
        cypher = response['response'].strip()
        
        # Clean up markdown formatting if present
        cypher = cypher.replace('```cypher', '').replace('```', '').strip()
        
        return cypher
    
    def generate_sql(self, natural_language_query):
        """Generate SQL query from natural language"""
        
        prompt = f"""You are a PostgreSQL expert. Convert this natural language query into a valid SQL query for the mythos_db database.

Query: {natural_language_query}

Respond with ONLY the SQL query, no explanations. Use proper PostgreSQL syntax."""

        response = self.ollama.generate(model=self.model, prompt=prompt)
        sql = response['response'].strip()
        
        # Clean up markdown formatting if present
        sql = sql.replace('```sql', '').replace('```', '').strip()
        
        return sql
    
    def execute_neo4j(self, cypher_query):
        """Execute Cypher query against Neo4j"""
        with self.neo4j_driver.session() as session:
            result = session.run(cypher_query)
            return [dict(record) for record in result]
    
    def execute_postgres(self, sql_query):
        """Execute SQL query against PostgreSQL"""
        cursor = self.pg_conn.cursor()
        cursor.execute(sql_query)
        
        if sql_query.strip().upper().startswith('SELECT'):
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            return [dict(zip(columns, row)) for row in results]
        else:
            self.pg_conn.commit()
            return {"status": "success", "rows_affected": cursor.rowcount}
    
    def query(self, natural_language_query):
        """Main query interface"""
        print(f"\n🔍 Query: {natural_language_query}")
        
        # Route to appropriate database
        db_type = self.route_query(natural_language_query)
        print(f"📊 Routing to: {db_type.upper()}")
        
        try:
            if db_type == 'neo4j':
                cypher = self.generate_cypher(natural_language_query)
                print(f"⚡ Cypher: {cypher}")
                results = self.execute_neo4j(cypher)
            else:
                sql = self.generate_sql(natural_language_query)
                print(f"⚡ SQL: {sql}")
                results = self.execute_postgres(sql)
            
            print(f"\n✅ Results:\n{json.dumps(results, indent=2, default=str)}\n")
            return results
            
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            return None
    
    def close(self):
        """Clean up connections"""
        self.neo4j_driver.close()
        self.pg_conn.close()

# CLI Interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 db_manager.py \"your natural language query\"")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    manager = MythosManager()
    manager.query(query)
    manager.close()

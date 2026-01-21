#!/usr/bin/env python3
"""
Database Manager - Natural language interface to Neo4j and PostgreSQL
"""

import os
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase
import psycopg2
from ollama import Client

# Load environment variables
load_dotenv('/opt/mythos/.env')

class DatabaseManager:
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
        
        # Current user context
        self.current_user = None
        
        # Load system prompt from file
        prompt_path = os.path.expanduser('~/main-vault/systems/arcturus/prompts/db_mode_prompt.md')
        try:
            with open(prompt_path, 'r') as f:
                self.system_prompt = f.read()
            print(f"✅ Loaded system prompt from {prompt_path}")
        except FileNotFoundError:
            print(f"⚠️  Warning: Could not find prompt file at {prompt_path}")
            print("    Using fallback minimal prompt")
            # Minimal fallback prompt
            self.system_prompt = """
You are a Neo4j Cypher expert. Generate valid Cypher queries.

Key relationships:
- (parent:Person)-[:PARENT_OF]->(child:Person)
- (Person)-[:SPOUSE_OF]-(Person)
- (Soul)-[:INCARNATED_AS]->(Lifetime)-[:EMBODIED_BY]->(Person)

Always return full nodes: RETURN n, not RETURN n.property
"""
    
    def set_user(self, user_info):
        """Set current user context"""
        self.current_user = user_info
    
    def route_query(self, natural_language_query):
        """Determine which database to use based on query content"""
        
        postgres_keywords = ['table', 'column', 'row', 'schema', 'index', 'view', 'user', 'chat', 'message']
        query_lower = natural_language_query.lower()
        
        if any(keyword in query_lower for keyword in postgres_keywords):
            return 'postgres'
        
        return 'neo4j'
    
    def generate_cypher(self, natural_language_query):
        """Generate Cypher query from natural language"""
        
        prompt = f"""{self.system_prompt}

Query: {natural_language_query}

Respond with ONLY the Cypher query, no markdown, no explanations."""

        response = self.ollama.generate(model=self.model, prompt=prompt)
        cypher = response['response'].strip()
        cypher = cypher.replace('```cypher', '').replace('```', '').strip()
        
        return cypher
    
    def format_neo4j_result(self, result, cypher):
        """Format Neo4j results for readable Telegram display"""
        
        if not result:
            return "No results found."
        
        # If it's a count query
        if 'count' in cypher.lower() and len(result) < 10:
            output = "📊 Node Counts:\n\n"
            for record in result:
                node_type = record.get('type', 'Unknown')
                count = record.get('count', 0)
                output += f"• {node_type}: {count}\n"
            return output
        
        # If returning full nodes, extract key properties
        output = ""
        for i, record in enumerate(result[:5], 1):  # Limit to first 5 results
            output += f"\n━━━ Result {i} ━━━\n"
            
            for key, value in record.items():
                # Handle node objects
                if hasattr(value, 'labels') and hasattr(value, '_properties'):
                    # It's a Neo4j node
                    labels = ', '.join(value.labels)
                    output += f"\n🏷️ {labels} Node:\n"
                    
                    # Show key properties only
                    props = dict(value._properties)

                    # Different properties for different node types
                    if 'Soul' in labels:
                        important_props = ['display_name', 'primary_role', 'canonical_id']
                    elif 'Person' in labels:
                        important_props = ['full_name', 'known_as', 'birth_date', 'birth_location', 'current_location']
                    elif 'Lifetime' in labels:
                        important_props = ['title', 'role', 'time_period', 'is_current']
                    else:
                        important_props = ['canonical_id', 'display_name', 'full_name', 'title']

                    for prop in important_props:
                        if prop in props:
                            output += f"  • {prop}: {props[prop]}\n"
                
                # Handle relationships
                elif hasattr(value, 'type'):
                    output += f"  → Relationship: {value.type}\n"
                
                # Handle simple values
                else:
                    output += f"{key}: {value}\n"
        
        if len(result) > 5:
            output += f"\n... and {len(result) - 5} more results"
        
        return output
    
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
        """
        Main query interface - returns formatted string for Telegram
        """
        
        # Route to appropriate database
        db_type = self.route_query(natural_language_query)
        
        try:
            if db_type == 'neo4j':
                cypher = self.generate_cypher(natural_language_query)
                results = self.execute_neo4j(cypher)
                
                # Format for display
                formatted = self.format_neo4j_result(results, cypher)
                
                response = f"🔍 Query: {natural_language_query}\n\n"
                response += f"⚡️ Cypher: {cypher}\n\n"
                response += formatted
                
                return response
            
            else:  # postgres
                sql = self.generate_sql(natural_language_query)
                results = self.execute_postgres(sql)
                
                response = f"🔍 Query: {natural_language_query}\n\n"
                response += f"⚡️ SQL: {sql}\n\n"
                response += f"✅ Results:\n{json.dumps(results, indent=2, default=str)}"
                
                return response
            
        except Exception as e:
            return f"❌ Error: {str(e)}\n\nQuery: {natural_language_query}"
    
    def generate_sql(self, natural_language_query):
        """Generate SQL query from natural language"""
        
        prompt = f"""You are a PostgreSQL expert. Convert this query to SQL for mythos_db.

Available tables: users, chat_messages

Query: {natural_language_query}

Respond with ONLY the SQL query, no markdown, no explanations."""

        response = self.ollama.generate(model=self.model, prompt=prompt)
        sql = response['response'].strip()
        sql = sql.replace('```sql', '').replace('```', '').strip()
        
        return sql
    
    def close(self):
        """Clean up connections"""
        self.neo4j_driver.close()
        self.pg_conn.close()

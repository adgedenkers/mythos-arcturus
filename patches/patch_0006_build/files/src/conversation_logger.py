"""
Conversation Logger
Logs all LLM interactions to Neo4j for learning and audit trail
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from neo4j import GraphDatabase


def log_conversation(
    question: str,
    answer: str,
    tools_used: List[str],
    conversation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Log a conversation to Neo4j
    
    Args:
        question: User's question
        answer: LLM's answer
        tools_used: List of diagnostic tools used
        conversation_id: Optional conversation ID for threading
        metadata: Optional additional metadata
    
    Returns:
        Conversation ID
    """
    # Get Neo4j connection from environment
    uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
    user = os.environ.get('NEO4J_USER', 'neo4j')
    password = os.environ.get('NEO4J_PASSWORD')
    
    if not password:
        # Silent fail - don't break if Neo4j not available
        return str(uuid.uuid4())
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            conv_id = conversation_id or str(uuid.uuid4())
            
            session.execute_write(
                _create_conversation_node,
                conv_id,
                question,
                answer,
                tools_used,
                metadata or {}
            )
            
            return conv_id
    except Exception as e:
        # Silent fail - logging shouldn't break the main flow
        print(f"Warning: Could not log conversation: {e}")
        return str(uuid.uuid4())
    finally:
        driver.close()


def _create_conversation_node(tx, conv_id, question, answer, tools_used, metadata):
    """Transaction: Create conversation node in Neo4j"""
    
    # Create conversation node
    tx.run("""
        CREATE (c:Conversation {
            id: $conv_id,
            timestamp: datetime(),
            question: $question,
            answer: $answer,
            tools_used: $tools_used,
            metadata: $metadata
        })
        
        // Link to System
        MERGE (sys:System {name: 'localhost'})
        CREATE (sys)-[:HAD_CONVERSATION]->(c)
    """, conv_id=conv_id, question=question, answer=answer,
         tools_used=tools_used, metadata=metadata)
    
    # Link to any events or services mentioned
    # This enables pattern learning: "what questions led to discovering this issue?"
    
    # Extract service names mentioned in question
    common_services = ['neo4j', 'postgresql', 'mythos_api', 'mythos_bot', 'ollama']
    for service in common_services:
        if service in question.lower() or service in answer.lower():
            tx.run("""
                MATCH (c:Conversation {id: $conv_id})
                MATCH (s:Service {name: $service})
                MERGE (c)-[:MENTIONED]->(s)
            """, conv_id=conv_id, service=service)
    
    # Link to recent events if tools were used
    if tools_used:
        tx.run("""
            MATCH (c:Conversation {id: $conv_id})
            MATCH (e:Event)
            WHERE e.timestamp > datetime() - duration({minutes: 5})
            MERGE (c)-[:REFERENCED]->(e)
        """, conv_id=conv_id)


def get_conversation_history(conversation_id: str, limit: int = 10) -> List[Dict]:
    """Get conversation history for context"""
    uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
    user = os.environ.get('NEO4J_USER', 'neo4j')
    password = os.environ.get('NEO4J_PASSWORD')
    
    if not password:
        return []
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (c:Conversation {id: $conv_id})
                RETURN c.question AS question,
                       c.answer AS answer,
                       c.timestamp AS timestamp
                ORDER BY c.timestamp DESC
                LIMIT $limit
            """, conv_id=conversation_id, limit=limit)
            
            return [dict(record) for record in result]
    except Exception:
        return []
    finally:
        driver.close()


def get_recent_conversations(hours: int = 24, limit: int = 20) -> List[Dict]:
    """Get recent conversations for analysis"""
    uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
    user = os.environ.get('NEO4J_USER', 'neo4j')
    password = os.environ.get('NEO4J_PASSWORD')
    
    if not password:
        return []
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (c:Conversation)
                WHERE c.timestamp > datetime() - duration({hours: $hours})
                RETURN c.id AS id,
                       c.question AS question,
                       c.answer AS answer,
                       c.tools_used AS tools_used,
                       c.timestamp AS timestamp
                ORDER BY c.timestamp DESC
                LIMIT $limit
            """, hours=hours, limit=limit)
            
            return [dict(record) for record in result]
    except Exception:
        return []
    finally:
        driver.close()

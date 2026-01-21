"""
Event Logger for Neo4j Graph
Writes system events as graph nodes with automatic causality linking
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError


class EventLogger:
    """Logs system events to Neo4j as graph nodes"""
    
    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j connection"""
        self.uri = uri
        self.user = user
        self.password = password
        self._driver = None
        self._connect()
    
    def _connect(self):
        """Establish Neo4j connection"""
        try:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Test connection
            with self._driver.session() as session:
                session.run("RETURN 1")
        except (ServiceUnavailable, AuthError) as e:
            raise ConnectionError(f"Failed to connect to Neo4j: {e}")
    
    def close(self):
        """Close Neo4j connection"""
        if self._driver:
            self._driver.close()
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> str:
        """
        Log an event to Neo4j graph
        
        Args:
            event_type: Type of event (e.g., "high_cpu", "service_failure")
            data: Event data as dictionary
            
        Returns:
            event_id: UUID of created event node
        """
        import uuid
        event_id = str(uuid.uuid4())
        
        with self._driver.session() as session:
            session.execute_write(
                self._create_event_tx,
                event_id,
                event_type,
                data
            )
        
        return event_id
    
    def _create_event_tx(self, tx, event_id: str, event_type: str, data: Dict[str, Any]):
        """Transaction: Create event node and link causality"""
        
        # Create event node
        tx.run("""
            CREATE (e:Event {
                id: $event_id,
                type: $event_type,
                timestamp: datetime(),
                data: $data
            })
            
            // Link to System node
            MERGE (sys:System {name: 'localhost'})
            CREATE (sys)-[:LOGGED]->(e)
        """, event_id=event_id, event_type=event_type, data=data)
        
        # Auto-link causality based on temporal proximity and event types
        self._link_causality(tx, event_id, event_type)
    
    def _link_causality(self, tx, event_id: str, event_type: str):
        """Link this event to recent events that may have caused it"""
        
        # Define which event types can cause others
        causal_relationships = {
            "high_memory": ["process_started", "high_cpu"],
            "service_failure": ["high_memory", "high_cpu", "low_disk", "connection_error"],
            "slow_query": ["high_memory", "high_cpu"],
            "connection_error": ["service_stopped", "network_issue"],
            "backup_failed": ["low_disk", "service_failure", "connection_error"]
        }
        
        # Get potential causes for this event type
        potential_causes = causal_relationships.get(event_type, [])
        
        if not potential_causes:
            return
        
        # Link to recent events of those types (within 30 seconds)
        tx.run("""
            MATCH (e:Event {id: $event_id})
            MATCH (prev:Event)
            WHERE prev.type IN $potential_causes
              AND prev.timestamp > datetime() - duration({seconds: 30})
              AND prev.timestamp < e.timestamp
              AND NOT (prev)-[:CAUSED]->(e)
            CREATE (prev)-[:MAY_HAVE_CAUSED]->(e)
        """, event_id=event_id, potential_causes=potential_causes)
    
    def log_metric(self, metric_type: str, value: float, unit: str = ""):
        """
        Log a simple metric (for time-series data)
        
        Args:
            metric_type: Type of metric (e.g., "cpu_percent")
            value: Numeric value
            unit: Unit of measurement (e.g., "percent", "MB")
        """
        with self._driver.session() as session:
            session.execute_write(
                self._create_metric_tx,
                metric_type,
                value,
                unit
            )
    
    def _create_metric_tx(self, tx, metric_type: str, value: float, unit: str):
        """Transaction: Create metric snapshot"""
        tx.run("""
            MERGE (sys:System {name: 'localhost'})
            CREATE (m:Metric {
                type: $metric_type,
                value: $value,
                unit: $unit,
                timestamp: datetime()
            })
            CREATE (sys)-[:HAS_METRIC]->(m)
        """, metric_type=metric_type, value=value, unit=unit)
    
    def log_process_state(self, pid: int, name: str, memory_mb: float, cpu_percent: float):
        """Log current state of a process"""
        with self._driver.session() as session:
            session.execute_write(
                self._update_process_tx,
                pid,
                name,
                memory_mb,
                cpu_percent
            )
    
    def _update_process_tx(self, tx, pid: int, name: str, memory_mb: float, cpu_percent: float):
        """Transaction: Update or create process node"""
        tx.run("""
            MERGE (sys:System {name: 'localhost'})
            MERGE (p:Process {pid: $pid})
            SET p.name = $name,
                p.memory_mb = $memory_mb,
                p.cpu_percent = $cpu_percent,
                p.last_seen = datetime(),
                p.status = 'active'
            
            MERGE (sys)-[:RUNS]->(p)
        """, pid=pid, name=name, memory_mb=memory_mb, cpu_percent=cpu_percent)
    
    def log_service_state(self, service_name: str, status: str, substate: str = ""):
        """Log systemd service state"""
        with self._driver.session() as session:
            session.execute_write(
                self._update_service_tx,
                service_name,
                status,
                substate
            )
    
    def _update_service_tx(self, tx, service_name: str, status: str, substate: str):
        """Transaction: Update or create service node"""
        tx.run("""
            MERGE (sys:System {name: 'localhost'})
            MERGE (s:Service {name: $service_name})
            SET s.status = $status,
                s.substate = $substate,
                s.last_checked = datetime()
            
            MERGE (sys)-[:RUNS_SERVICE]->(s)
        """, service_name=service_name, status=status, substate=substate)
    
    def get_recent_events(self, minutes: int = 5, event_type: Optional[str] = None) -> List[Dict]:
        """
        Get recent events from graph
        
        Args:
            minutes: Look back this many minutes
            event_type: Filter by event type (optional)
            
        Returns:
            List of event dictionaries
        """
        with self._driver.session() as session:
            result = session.run("""
                MATCH (e:Event)
                WHERE e.timestamp > datetime() - duration({minutes: $minutes})
                """ + (f"AND e.type = '{event_type}'" if event_type else "") + """
                RETURN e.id AS id,
                       e.type AS type,
                       e.timestamp AS timestamp,
                       e.data AS data
                ORDER BY e.timestamp DESC
            """, minutes=minutes)
            
            return [dict(record) for record in result]
    
    def trace_causality(self, event_id: str) -> List[Dict]:
        """
        Trace the causal chain for an event
        
        Args:
            event_id: ID of event to trace
            
        Returns:
            List of events in causal chain
        """
        with self._driver.session() as session:
            result = session.run("""
                MATCH (target:Event {id: $event_id})
                MATCH path = (root:Event)-[:MAY_HAVE_CAUSED*0..5]->(target)
                WHERE NOT (()-[:MAY_HAVE_CAUSED]->(root))
                RETURN [node IN nodes(path) | {
                    id: node.id,
                    type: node.type,
                    timestamp: node.timestamp,
                    data: node.data
                }] AS causal_chain
                ORDER BY length(path) DESC
                LIMIT 1
            """, event_id=event_id)
            
            record = result.single()
            if record:
                return record["causal_chain"]
            return []


class EventLoggerFactory:
    """Factory for creating EventLogger instances"""
    
    _instance = None
    
    @classmethod
    def get_logger(cls, uri: str = None, user: str = None, password: str = None) -> EventLogger:
        """Get or create EventLogger instance (singleton pattern)"""
        if cls._instance is None:
            # Get from environment if not provided
            uri = uri or os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
            user = user or os.environ.get('NEO4J_USER', 'neo4j')
            password = password or os.environ.get('NEO4J_PASSWORD')
            
            if not password:
                raise ValueError("NEO4J_PASSWORD not provided and not in environment")
            
            cls._instance = EventLogger(uri, user, password)
        
        return cls._instance
    
    @classmethod
    def close_logger(cls):
        """Close the logger connection"""
        if cls._instance:
            cls._instance.close()
            cls._instance = None

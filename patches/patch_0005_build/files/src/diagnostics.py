"""
AI Diagnostics Interface
Provides structured query interface for AI/LLM to diagnose system issues
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from neo4j import GraphDatabase


class Diagnostics:
    """Query interface for AI-powered system diagnostics"""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """Initialize Neo4j connection"""
        self.uri = uri or os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.environ.get('NEO4J_USER', 'neo4j')
        self.password = password or os.environ.get('NEO4J_PASSWORD')
        
        if not self.password:
            raise ValueError("NEO4J_PASSWORD required")
        
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
    
    def close(self):
        """Close connection"""
        if self.driver:
            self.driver.close()
    
    def get_system_health(self) -> Dict:
        """
        Get overall system health status
        Returns single dict with current metrics and recent issues
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (sys:System {name: 'localhost'})
                
                // Get recent issues (last 5 minutes)
                OPTIONAL MATCH (sys)-[:LOGGED]->(event:Event)
                WHERE event.timestamp > datetime() - duration({minutes: 5})
                  AND event.type IN ['high_cpu', 'high_memory', 'low_disk', 
                                      'service_failure', 'service_stopped']
                
                // Get active processes
                OPTIONAL MATCH (sys)-[:RUNS]->(proc:Process)
                WHERE proc.last_seen > datetime() - duration({minutes: 2})
                
                // Get service statuses
                OPTIONAL MATCH (sys)-[:RUNS_SERVICE]->(svc:Service)
                
                RETURN {
                    timestamp: datetime(),
                    active_processes: count(DISTINCT proc),
                    recent_issues: collect(DISTINCT {
                        type: event.type,
                        timestamp: event.timestamp,
                        data: event.data
                    }),
                    services: collect(DISTINCT {
                        name: svc.name,
                        status: svc.status
                    }),
                    health_score: CASE 
                        WHEN count(DISTINCT event) = 0 THEN 100
                        WHEN count(DISTINCT event) <= 2 THEN 80
                        WHEN count(DISTINCT event) <= 5 THEN 60
                        ELSE 40
                    END
                } AS health
            """)
            
            record = result.single()
            if record:
                return dict(record["health"])
            return {"health_score": 0, "error": "No system data found"}
    
    def trace_failure(self, service_name: str = None, event_id: str = None) -> Dict:
        """
        Trace the root cause of a failure
        
        Args:
            service_name: Name of failed service (optional)
            event_id: Specific event ID to trace (optional)
        
        Returns:
            Dict with causal chain from root cause to failure
        """
        with self.driver.session() as session:
            if event_id:
                # Trace specific event
                result = session.run("""
                    MATCH (failure:Event {id: $event_id})
                    
                    // Find causal chain
                    OPTIONAL MATCH path = (root:Event)-[:MAY_HAVE_CAUSED*0..5]->(failure)
                    WHERE NOT (()-[:MAY_HAVE_CAUSED]->(root))
                    
                    WITH path, nodes(path) AS chain
                    ORDER BY length(path) DESC
                    LIMIT 1
                    
                    RETURN {
                        failure_event: {
                            id: failure.id,
                            type: failure.type,
                            timestamp: failure.timestamp,
                            data: failure.data
                        },
                        causal_chain: [node IN chain | {
                            type: node.type,
                            timestamp: node.timestamp,
                            data: node.data
                        }],
                        root_cause: chain[0] {
                            .type,
                            .timestamp,
                            .data
                        },
                        confidence: CASE 
                            WHEN length(path) = 0 THEN 0.5
                            WHEN length(path) <= 2 THEN 0.9
                            ELSE 0.7
                        END
                    } AS trace
                """, event_id=event_id)
            
            elif service_name:
                # Find most recent failure for this service
                result = session.run("""
                    MATCH (failure:Event)
                    WHERE failure.type = 'service_failure'
                      AND failure.data.service = $service_name
                    
                    WITH failure
                    ORDER BY failure.timestamp DESC
                    LIMIT 1
                    
                    // Find causal chain
                    OPTIONAL MATCH path = (root:Event)-[:MAY_HAVE_CAUSED*0..5]->(failure)
                    WHERE NOT (()-[:MAY_HAVE_CAUSED]->(root))
                    
                    WITH path, nodes(path) AS chain, failure
                    ORDER BY length(path) DESC
                    LIMIT 1
                    
                    RETURN {
                        service: $service_name,
                        failure_event: {
                            id: failure.id,
                            type: failure.type,
                            timestamp: failure.timestamp,
                            data: failure.data
                        },
                        causal_chain: [node IN chain | {
                            type: node.type,
                            timestamp: node.timestamp,
                            data: node.data
                        }],
                        root_cause: CASE WHEN chain IS NOT NULL AND size(chain) > 0
                            THEN chain[0] {.type, .timestamp, .data}
                            ELSE null
                        END,
                        confidence: CASE 
                            WHEN path IS NULL THEN 0.3
                            WHEN length(path) = 0 THEN 0.5
                            WHEN length(path) <= 2 THEN 0.9
                            ELSE 0.7
                        END
                    } AS trace
                """, service_name=service_name)
            
            else:
                return {"error": "Must provide either service_name or event_id"}
            
            record = result.single()
            if record:
                return dict(record["trace"])
            return {"error": "No failure found"}
    
    def get_recent_events(self, 
                          minutes: int = 60, 
                          event_types: Optional[List[str]] = None,
                          limit: int = 50) -> List[Dict]:
        """
        Get recent events
        
        Args:
            minutes: Look back this many minutes
            event_types: Filter by event types (optional)
            limit: Max number of events to return
        
        Returns:
            List of event dicts
        """
        with self.driver.session() as session:
            type_filter = ""
            if event_types:
                types_str = "', '".join(event_types)
                type_filter = f"AND e.type IN ['{types_str}']"
            
            result = session.run(f"""
                MATCH (e:Event)
                WHERE e.timestamp > datetime() - duration({{minutes: $minutes}})
                {type_filter}
                
                RETURN {{
                    id: e.id,
                    type: e.type,
                    timestamp: e.timestamp,
                    data: e.data
                }} AS event
                ORDER BY e.timestamp DESC
                LIMIT $limit
            """, minutes=minutes, limit=limit)
            
            return [dict(r["event"]) for r in result]
    
    def get_service_status(self, service_name: str = None) -> Dict:
        """
        Get current status of service(s)
        
        Args:
            service_name: Specific service (optional, returns all if not provided)
        
        Returns:
            Dict with service status info
        """
        with self.driver.session() as session:
            if service_name:
                result = session.run("""
                    MATCH (s:Service {name: $service_name})
                    
                    // Get recent events for this service
                    OPTIONAL MATCH (e:Event)
                    WHERE (e.type = 'service_failure' OR e.type = 'service_stopped')
                      AND e.data.service = $service_name
                      AND e.timestamp > datetime() - duration({hours: 24})
                    
                    WITH s, e
                    ORDER BY e.timestamp DESC
                    
                    RETURN {
                        name: s.name,
                        status: s.status,
                        substate: s.substate,
                        last_checked: s.last_checked,
                        recent_issues: collect({
                            type: e.type,
                            timestamp: e.timestamp
                        })[0..5]
                    } AS service
                """, service_name=service_name)
                
                record = result.single()
                if record:
                    return dict(record["service"])
                return {"error": f"Service not found: {service_name}"}
            
            else:
                # Return all services
                result = session.run("""
                    MATCH (s:Service)
                    RETURN {
                        name: s.name,
                        status: s.status,
                        substate: s.substate,
                        last_checked: s.last_checked
                    } AS service
                    ORDER BY s.name
                """)
                
                return {"services": [dict(r["service"]) for r in result]}
    
    def get_high_resource_processes(self, 
                                   memory_threshold: float = 10.0,
                                   cpu_threshold: float = 50.0) -> List[Dict]:
        """
        Get processes using high resources
        
        Args:
            memory_threshold: Memory percent threshold
            cpu_threshold: CPU percent threshold
        
        Returns:
            List of process dicts
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Process)
                WHERE p.last_seen > datetime() - duration({minutes: 2})
                  AND (p.memory_percent > $memory_threshold 
                       OR p.cpu_percent > $cpu_threshold)
                
                RETURN {
                    pid: p.pid,
                    name: p.name,
                    memory_mb: p.memory_mb,
                    cpu_percent: p.cpu_percent,
                    last_seen: p.last_seen
                } AS process
                ORDER BY p.memory_mb DESC
            """, memory_threshold=memory_threshold, cpu_threshold=cpu_threshold)
            
            return [dict(r["process"]) for r in result]
    
    def predict_failure(self, service_name: str, lookback_days: int = 30) -> Dict:
        """
        Predict potential failure based on historical patterns
        
        Args:
            service_name: Service to analyze
            lookback_days: How far back to look for patterns
        
        Returns:
            Dict with prediction info
        """
        with self.driver.session() as session:
            result = session.run("""
                // Find historical failures for this service
                MATCH (failure:Event)
                WHERE failure.type = 'service_failure'
                  AND failure.data.service = $service_name
                  AND failure.timestamp > datetime() - duration({days: $lookback_days})
                
                // What preceded these failures?
                MATCH (warning:Event)-[:MAY_HAVE_CAUSED*1..3]->(failure)
                WHERE warning.timestamp < failure.timestamp
                
                WITH warning.type AS warning_type, 
                     count(*) AS occurrences,
                     avg(duration.between(warning.timestamp, failure.timestamp).seconds) AS avg_lead_time
                ORDER BY occurrences DESC
                LIMIT 5
                
                // Check if these warning types exist currently
                MATCH (current:Event)
                WHERE current.type = warning_type
                  AND current.timestamp > datetime() - duration({minutes: 30})
                
                RETURN {
                    service: $service_name,
                    warning_patterns: collect(DISTINCT {
                        warning_type: warning_type,
                        historical_count: occurrences,
                        avg_lead_time_seconds: avg_lead_time,
                        currently_present: count(current) > 0
                    }),
                    risk_level: CASE
                        WHEN count(current) > 0 THEN 'HIGH'
                        ELSE 'LOW'
                    END,
                    confidence: CASE
                        WHEN occurrences > 5 THEN 0.9
                        WHEN occurrences > 2 THEN 0.7
                        ELSE 0.5
                    END
                } AS prediction
            """, service_name=service_name, lookback_days=lookback_days)
            
            record = result.single()
            if record:
                return dict(record["prediction"])
            return {
                "service": service_name,
                "risk_level": "UNKNOWN",
                "message": "Insufficient historical data"
            }
    
    def query(self, cypher: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """
        Execute arbitrary Cypher query (for advanced AI queries)
        
        Args:
            cypher: Cypher query string
            parameters: Query parameters (optional)
        
        Returns:
            List of result records
        """
        with self.driver.session() as session:
            result = session.run(cypher, parameters or {})
            return [dict(record) for record in result]


# Convenience functions for quick diagnostics

def check_system_health(uri: str = None, user: str = None, password: str = None) -> Dict:
    """Quick system health check"""
    diag = Diagnostics(uri, user, password)
    try:
        return diag.get_system_health()
    finally:
        diag.close()


def why_did_service_fail(service_name: str, 
                        uri: str = None, 
                        user: str = None, 
                        password: str = None) -> Dict:
    """Quick failure trace for a service"""
    diag = Diagnostics(uri, user, password)
    try:
        return diag.trace_failure(service_name=service_name)
    finally:
        diag.close()

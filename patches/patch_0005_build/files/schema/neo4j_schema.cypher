// Arcturus Graph Logging Schema
// Creates indexes and initial System node

// Create indexes for fast queries
CREATE INDEX event_timestamp IF NOT EXISTS FOR (e:Event) ON (e.timestamp);
CREATE INDEX event_type IF NOT EXISTS FOR (e:Event) ON (e.type);
CREATE INDEX event_id IF NOT EXISTS FOR (e:Event) ON (e.id);
CREATE INDEX process_pid IF NOT EXISTS FOR (p:Process) ON (p.pid);
CREATE INDEX service_name IF NOT EXISTS FOR (s:Service) ON (s.name);
CREATE INDEX metric_timestamp IF NOT EXISTS FOR (m:Metric) ON (m.timestamp);

// Create System node if it doesn't exist
MERGE (sys:System {name: 'localhost'})
ON CREATE SET
    sys.created = datetime(),
    sys.hostname = 'arcturus',
    sys.monitoring_enabled = true
ON MATCH SET
    sys.monitoring_enabled = true,
    sys.last_schema_update = datetime();

// Return confirmation
MATCH (sys:System {name: 'localhost'})
RETURN sys.name AS system, 
       sys.created AS created,
       sys.monitoring_enabled AS monitoring_enabled;

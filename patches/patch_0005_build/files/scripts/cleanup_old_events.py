#!/usr/bin/env python3
"""
Cleanup Old Events
Removes events older than retention period from Neo4j
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from neo4j import GraphDatabase

# Setup logging
log_file = "/opt/mythos/graph_logging/logs/cleanup.log"
Path(log_file).parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('EventCleanup')


def cleanup_old_events(retention_days: int = 10):
    """
    Remove events older than retention period
    
    Args:
        retention_days: Keep events newer than this many days
    """
    # Get Neo4j connection from environment
    uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
    user = os.environ.get('NEO4J_USER', 'neo4j')
    password = os.environ.get('NEO4J_PASSWORD')
    
    if not password:
        logger.error("NEO4J_PASSWORD not set")
        return 1
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            # Count events to be deleted
            result = session.run("""
                MATCH (e:Event)
                WHERE e.timestamp < datetime() - duration({days: $days})
                RETURN count(e) AS count
            """, days=retention_days)
            
            count_to_delete = result.single()["count"]
            
            if count_to_delete == 0:
                logger.info(f"No events older than {retention_days} days found")
                return 0
            
            logger.info(f"Deleting {count_to_delete} events older than {retention_days} days")
            
            # Delete old events
            result = session.run("""
                MATCH (e:Event)
                WHERE e.timestamp < datetime() - duration({days: $days})
                DETACH DELETE e
                RETURN count(e) AS deleted
            """, days=retention_days)
            
            deleted_count = result.single()["deleted"]
            logger.info(f"Successfully deleted {deleted_count} old events")
            
            # Also clean up old metric snapshots
            result = session.run("""
                MATCH (m:Metric)
                WHERE m.timestamp < datetime() - duration({days: $days})
                DETACH DELETE m
                RETURN count(m) AS deleted
            """, days=retention_days)
            
            metric_count = result.single()["deleted"]
            if metric_count > 0:
                logger.info(f"Deleted {metric_count} old metric snapshots")
            
            # Clean up orphaned process nodes (not seen in 7 days)
            result = session.run("""
                MATCH (p:Process)
                WHERE p.last_seen < datetime() - duration({days: 7})
                DETACH DELETE p
                RETURN count(p) AS deleted
            """)
            
            process_count = result.single()["deleted"]
            if process_count > 0:
                logger.info(f"Deleted {process_count} orphaned process nodes")
            
            # Log total cleanup
            logger.info(
                f"Cleanup complete: {deleted_count} events, "
                f"{metric_count} metrics, {process_count} processes removed"
            )
            
            return 0
    
    except Exception as e:
        logger.error(f"Cleanup failed: {e}", exc_info=True)
        return 1
    
    finally:
        driver.close()


def main():
    """Main entry point"""
    # Get retention period from environment or use default
    retention_days = int(os.environ.get('EVENT_RETENTION_DAYS', '10'))
    
    logger.info(f"Starting event cleanup (retention: {retention_days} days)")
    return cleanup_old_events(retention_days)


if __name__ == '__main__':
    sys.exit(main())

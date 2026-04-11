import json
import redis
import psycopg2
from datetime import datetime

from perception_event_types import EVENT_TYPES

REDIS_STREAM = "mythos:perception"

class PerceptionRouter:

    def __init__(self, pg_conn_string, redis_host="localhost", redis_port=6379):
        self.pg_conn = psycopg2.connect(pg_conn_string)
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )

    def log_event(
        self,
        event_type,
        content,
        source=None,
        metadata=None
    ):

        if event_type not in EVENT_TYPES:
            raise ValueError(f"Invalid perception event type: {event_type}")

        timestamp = datetime.utcnow()

        payload = {
            "event_type": event_type,
            "content": content,
            "source": source,
            "metadata": metadata or {},
            "timestamp": timestamp.isoformat()
        }

        event_id = self._store_event(payload)

        payload["event_id"] = event_id

        self.redis.xadd(
            REDIS_STREAM,
            payload
        )

        return event_id

    def _store_event(self, payload):

        with self.pg_conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO perception_log
                (source, source_platform, content, raw_data)
                VALUES (%s,%s,%s,%s)
                RETURNING id
                """,
                (
                    payload["event_type"],
                    payload["content"],
                    payload["source"],
                    json.dumps(payload["metadata"]),
                    payload["timestamp"]
                )
            )

            event_id = cur.fetchone()[0]

        self.pg_conn.commit()

        return event_id

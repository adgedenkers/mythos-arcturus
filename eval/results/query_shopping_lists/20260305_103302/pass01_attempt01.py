import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from engine.base import SkillBase, SkillRequest, SkillResponse

load_dotenv()

def _get_conn():
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'mythos'),
            user=os.getenv('DB_USER', 'mythos'),
            password=os.getenv('DB_PASSWORD', ''),
            port=os.getenv('DB_PORT', '5432'),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        if conn:
            conn.close()
        raise e

class QueryShoppingListsSkill(SkillBase):
    name = 'query_shopping_lists'
    triggers = [
        'shopping',
        'shopping list',
        'groceries',
        'grocery list',
        'what do I need to buy',
        'need to get',
        'shopping items'
    ]
    cache_ttl = 300

    def execute(self, request: SkillRequest) -> SkillResponse:
        pass

    def _query_lists(self, conn):
        pass

    def _query_items(self, conn, list_ids):
        pass

    def _format_results(self, lists, items):
        pass

    def _build_summary(self, lists, items):
        pass
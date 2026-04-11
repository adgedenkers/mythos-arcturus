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
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, status, created_at 
                    FROM shopping_lists 
                    WHERE is_active = true 
                    ORDER BY created_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error querying shopping lists: {e}")
            raise e
        finally:
            if conn:
                conn.close()

    def _query_items(self, conn, list_ids):
        try:
            with conn.cursor() as cursor:
                # Convert UUIDs to strings for the query
                list_id_strs = [str(list_id) for list_id in list_ids]
                # Build the query with proper parameterization
                placeholders = ','.join(['%s'] * len(list_id_strs))
                query = f"""
                    SELECT sli.id, si.name as item_name, si.department, 
                           sli.quantity, sli.priority, sli.completed, sli.notes
                    FROM shopping_list_items sli 
                    JOIN shopping_items si ON si.id = sli.item_id 
                    WHERE sli.list_id IN ({placeholders}) 
                    ORDER BY sli.completed, si.department, si.name
                """
                cursor.execute(query, list_id_strs)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error querying shopping items: {e}")
            raise e
        finally:
            if conn:
                conn.close()

    def _format_results(self, lists, items):
        pass

    def _build_summary(self, lists, items):
        pass
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
        conn = _get_conn()
        try:
            lists = self._query_lists(conn)
            if not lists:
                return SkillResponse(text="No active shopping lists.")
            
            list_ids = [list_item['id'] for list_item in lists]
            items = self._query_items(conn, list_ids)
            
            formatted_results = self._format_results(lists, items)
            summary = self._build_summary(lists, items)
            
            return SkillResponse(
                skill_name=self.name,
                data={'lists': formatted_results, 'count': len(lists)},
                summary=summary,
                confidence=0.95,
                sources=['mythos.shopping_lists', 'mythos.shopping_items']
            )
        except Exception as e:
            logging.error(f"Error in execute method: {e}")
            raise e
        finally:
            if conn:
                conn.close()

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

    def _format_results(self, lists, items):
        # Group items by list_id
        items_by_list = {}
        for item in items:
            list_id = item['id']  # This is actually the list_id from the query
            if list_id not in items_by_list:
                items_by_list[list_id] = []
            items_by_list[list_id].append({
                'item_name': item['item_name'],
                'department': item['department'],
                'quantity': item['quantity'],
                'priority': item['priority'],
                'completed': item['completed'],
                'notes': item['notes']
            })
        
        # Format the lists with their items
        formatted_lists = []
        for list_item in lists:
            formatted_lists.append({
                'id': str(list_item['id']),
                'name': list_item['name'],
                'status': list_item['status'],
                'items': items_by_list.get(list_item['id'], [])
            })
        
        # Convert to string format
        result = []
        for list_item in formatted_lists:
            result.append(f"List: {list_item['name']}")
            if list_item['items']:
                for item in list_item['items']:
                    status = "✓" if item['completed'] else "○"
                    result.append(f"  {status} {item['item_name']} ({item['quantity']} {item['department']})")
            else:
                result.append("  (No items)")
            result.append("")
        
        return "\n".join(result)

    def _build_summary(self, lists, items):
        active_count = len(lists)
        if active_count == 0:
            return "You don't have any active shopping lists."
        
        # Get the first list (most recent)
        first_list = lists[0]
        first_list_id = first_list['id']
        
        # Count items for the first list
        first_list_items = [item for item in items if item['id'] == first_list_id]
        total_items = len(first_list_items)
        remaining_items = len([item for item in first_list_items if not item['completed']])
        
        summary = f"{active_count} active shopping list(s). {first_list['name']}: {total_items} items ({remaining_items} remaining)."
        
        # Show uncompleted items for the top list
        if first_list_items:
            uncompleted = [item for item in first_list_items if not item['completed']]
            if uncompleted:
                summary += "\n\nTop list items to get:"
                for item in uncompleted[:3]:  # Show top 3 items
                    summary += f"\n• {item['item_name']} ({item['quantity']} {item['department']})"
                if len(uncompleted) > 3:
                    summary += f"\n... and {len(uncompleted) - 3} more items"
        
        return summary
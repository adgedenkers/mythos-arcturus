"""
Backlog Analyst — Iris's daily intelligence system.

Runs the 32b model against the full state of life + work,
produces prioritized analysis, and delivers morning briefings.

Three trigger modes:
  1. Scheduled morning run (3:00 AM) → full analysis + Telegram briefing
  2. Post-patch trigger → re-analyze dependencies, DB update only
  3. On-demand via Iris → conversational response

Usage:
    from core.backlog_analyst import BacklogAnalyst
    analyst = BacklogAnalyst()
    
    # Morning briefing
    result = await analyst.run_analysis('morning')
    
    # Post-patch
    result = await analyst.run_analysis('post_patch')
    
    # On-demand (returns text for Iris to relay)
    result = await analyst.run_analysis('on_demand')
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta, date
from typing import Optional
import psycopg2
import psycopg2.extras
import httpx

logger = logging.getLogger(__name__)

# Database connection
DB_CONFIG = {
    'dbname': 'mythos',
    'user': 'postgres',
    'host': 'localhost'
}

OLLAMA_URL = "http://localhost:11434"
ANALYST_MODEL = "qwen2.5:32b"

ANALYST_SYSTEM_PROMPT = """You are Iris's analytical mind — the part that sees patterns, dependencies, and priorities.

You are analyzing the full state of Ka'tuar'el's life and work to produce a daily intelligence briefing.

Your job:
1. Look at everything — backlog, routines, calendar, bills, finances, recent events
2. Identify what matters TODAY specifically
3. Flag anything urgent (bills due, low balances, overdue items)
4. Recommend transfer amounts between accounts if any account will be short for upcoming bills
5. Prioritize the work backlog based on dependencies and what's unblocked
6. Note patterns you see (things consistently skipped, recurring issues, trends)

Output STRICT JSON with this structure:
{
    "briefing": "Natural language morning briefing, 3-5 sentences, conversational not robotic. This is what Iris sends to Telegram.",
    "priorities_today": ["Priority 1 description", "Priority 2", "Priority 3"],
    "urgent_flags": ["Any urgent items — bills due, low balances, overdue routines"],
    "transfer_recommendations": [
        {"from_account": "SUN", "to_account": "USAA", "amount": 300, "reason": "NYSEG due in 3 days, USAA balance insufficient"}
    ],
    "bills_due_7_days": [
        {"bill_name": "...", "amount": 0, "due_day": 0, "account": "...", "covered": true}
    ],
    "backlog_reorder": [
        {"item_id": 0, "new_priority": 0, "reason": "Now unblocked by X"}
    ],
    "pattern_observations": ["Any patterns noticed across recent data"],
    "items_unblocked": [0],
    "items_newly_blocked": [0],
    "accuracy_check": "If this is an evening run, how did the morning predictions hold up"
}

IMPORTANT:
- Be specific about dollar amounts and dates
- If accounts are fine, say so — don't manufacture urgency
- Transfer recommendations should be conservative — only when actually needed
- The briefing text should sound like a person who cares, not a dashboard
- Return ONLY valid JSON, no markdown fences, no preamble
"""


class BacklogAnalyst:
    """Iris's daily intelligence system."""

    def __init__(self):
        self.conn = None

    def _get_conn(self):
        """Get or create database connection."""
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**DB_CONFIG)
        return self.conn

    def _gather_state(self) -> dict:
        """Pull the full system state from Postgres."""
        conn = self._get_conn()
        state = {}

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Open backlog items, ordered by priority
            cur.execute("""
                SELECT id, title, description, status, priority_order, 
                       depends_on, blocked_by, phase, estimated_effort, category,
                       analyst_notes, last_analyzed
                FROM idea_backlog 
                WHERE status NOT IN ('done', 'cancelled')
                ORDER BY priority_order NULLS LAST, id
            """)
            state['backlog'] = [dict(r) for r in cur.fetchall()]

            # Recently completed (last 7 days)
            cur.execute("""
                SELECT id, title, description, updated_at
                FROM idea_backlog
                WHERE status = 'done'
                AND updated_at >= NOW() - INTERVAL '7 days'
                ORDER BY updated_at DESC
            """)
            state['recent_completions'] = [dict(r) for r in cur.fetchall()]

            # Today's routines + completion status
            today = date.today()
            day_name = today.strftime('%A').lower()  # monday, tuesday, etc
            cur.execute("""
                SELECT r.id, r.title, r.frequency, r.domain,
                       rc.status as completion_status, rc.completed_at
                FROM routines r
                LEFT JOIN routine_completions rc 
                    ON r.id = rc.routine_id 
                    AND rc.completion_date = %s
                WHERE r.active = true
                ORDER BY r.domain, r.title
            """, (today,))
            state['routines_today'] = [dict(r) for r in cur.fetchall()]

            # Calendar events today and next 3 days
            cur.execute("""
                SELECT id, title, event_date, person, notes
                FROM calendar_events
                WHERE event_date >= %s AND event_date <= %s
                ORDER BY event_date
            """, (today, today + timedelta(days=3)))
            state['calendar_upcoming'] = [dict(r) for r in cur.fetchall()]

            # Bills due in next 7 days
            today_day = today.day
            # Handle month wraparound
            days_to_check = []
            for i in range(7):
                d = today + timedelta(days=i)
                days_to_check.append(d.day)

            cur.execute("""
                SELECT id, merchant, expected_amount, due_day, frequency, category
                FROM recurring_bills
                WHERE active = true AND due_day = ANY(%s)
                ORDER BY due_day
            """, (days_to_check,))
            state['bills_due_7_days'] = [dict(r) for r in cur.fetchall()]

            # Account balances
            cur.execute("""
                SELECT id, account_name, abbreviation, account_type, current_balance
                FROM accounts
                ORDER BY id
            """)
            state['accounts'] = [dict(r) for r in cur.fetchall()]

            # Yesterday's checkin
            yesterday = today - timedelta(days=1)
            cur.execute("""
                SELECT id, checkin_date, mood, energy, notes, created_at
                FROM checkin_log
                WHERE checkin_date = %s
                ORDER BY created_at DESC LIMIT 1
            """, (yesterday,))
            row = cur.fetchone()
            state['yesterday_checkin'] = dict(row) if row else None

            # Recent life events (last 3 days)
            cur.execute("""
                SELECT id, domain, summary, person, created_at
                FROM life_events
                WHERE created_at >= NOW() - INTERVAL '3 days'
                ORDER BY created_at DESC
                LIMIT 20
            """)
            state['recent_life_events'] = [dict(r) for r in cur.fetchall()]

            # Last analysis (for accuracy tracking)
            cur.execute("""
                SELECT id, created_at, trigger_type, summary, predictions_made, predictions_correct
                FROM backlog_analysis
                ORDER BY created_at DESC LIMIT 1
            """)
            row = cur.fetchone()
            state['last_analysis'] = dict(row) if row else None

        return state

    def _build_prompt(self, state: dict, trigger_type: str) -> str:
        """Build the analysis prompt from system state."""
        today = date.today()
        
        prompt_parts = [
            f"TODAY: {today.strftime('%A, %B %d, %Y')}",
            f"TRIGGER: {trigger_type}",
            ""
        ]

        # Accounts
        prompt_parts.append("=== ACCOUNT BALANCES ===")
        for acct in state['accounts']:
            bal = acct.get('current_balance', 0) or 0
            prompt_parts.append(f"  {acct['abbreviation']}: ${bal:,.2f} ({acct['account_type']})")

        # Bills due next 7 days
        prompt_parts.append("\n=== BILLS DUE NEXT 7 DAYS ===")
        if state['bills_due_7_days']:
            for bill in state['bills_due_7_days']:
                amt = bill.get('expected_amount', 0) or 0
                prompt_parts.append(f"  {bill['merchant']}: ${amt:,.2f} (day {bill['due_day']})")
        else:
            prompt_parts.append("  No bills due in next 7 days.")

        # Today's routines
        prompt_parts.append("\n=== TODAY'S ROUTINES ===")
        for r in state['routines_today']:
            status = r.get('completion_status') or 'pending'
            prompt_parts.append(f"  [{status}] {r['title']} ({r['domain']})")

        # Calendar
        prompt_parts.append("\n=== CALENDAR (today + 3 days) ===")
        if state['calendar_upcoming']:
            for evt in state['calendar_upcoming']:
                person = f" ({evt['person']})" if evt.get('person') else ""
                prompt_parts.append(f"  {evt['event_date']}: {evt['title']}{person}")
        else:
            prompt_parts.append("  No upcoming calendar events.")

        # Yesterday's checkin
        prompt_parts.append("\n=== YESTERDAY'S CHECKIN ===")
        if state['yesterday_checkin']:
            ci = state['yesterday_checkin']
            mood = ci.get('mood', '?')
            energy = ci.get('energy', '?')
            notes = ci.get('notes', '')
            prompt_parts.append(f"  Mood: {mood}, Energy: {energy}")
            if notes:
                prompt_parts.append(f"  Notes: {notes}")
        else:
            prompt_parts.append("  No checkin recorded yesterday.")

        # Recent life events
        if state['recent_life_events']:
            prompt_parts.append("\n=== RECENT LIFE EVENTS (3 days) ===")
            for evt in state['recent_life_events'][:10]:
                prompt_parts.append(f"  [{evt.get('domain', '?')}] {evt.get('summary', '?')}")

        # Backlog
        prompt_parts.append("\n=== OPEN BACKLOG (ordered by priority) ===")
        for item in state['backlog'][:20]:
            deps = ""
            if item.get('depends_on'):
                deps = f" [depends on: {item['depends_on']}]"
            blocked = ""
            if item.get('blocked_by'):
                blocked = f" [BLOCKED by: {item['blocked_by']}]"
            priority = item.get('priority_order', '?')
            effort = item.get('estimated_effort', '?')
            prompt_parts.append(
                f"  #{priority} [id:{item['id']}] {item['title']} "
                f"({item.get('status', '?')}, {effort}){deps}{blocked}"
            )

        # Recent completions
        if state['recent_completions']:
            prompt_parts.append("\n=== COMPLETED LAST 7 DAYS ===")
            for item in state['recent_completions']:
                prompt_parts.append(f"  ✅ {item['title']}")

        # Last analysis accuracy
        if state['last_analysis']:
            la = state['last_analysis']
            prompt_parts.append(f"\n=== LAST ANALYSIS ===")
            prompt_parts.append(f"  {la['trigger_type']} on {la['created_at']}")
            if la.get('predictions_made'):
                prompt_parts.append(
                    f"  Predictions: {la['predictions_correct']}/{la['predictions_made']} correct"
                )

        return "\n".join(prompt_parts)

    async def _call_model(self, prompt: str) -> dict:
        """Call the 32b model with the analysis prompt."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": ANALYST_MODEL,
                    "messages": [
                        {"role": "system", "content": ANALYST_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 2000
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            raw_text = data.get("message", {}).get("content", "")

        # Parse JSON from response
        try:
            # Strip markdown fences if present
            clean = raw_text.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
            if clean.endswith("```"):
                clean = clean.rsplit("```", 1)[0]
            clean = clean.strip()
            
            result = json.loads(clean)
            result['_raw'] = raw_text
            return result
        except json.JSONDecodeError:
            logger.error(f"Failed to parse analyst response as JSON: {raw_text[:500]}")
            return {
                "briefing": "I tried to analyze today but couldn't parse my own thoughts. Check the logs.",
                "priorities_today": [],
                "urgent_flags": [],
                "transfer_recommendations": [],
                "bills_due_7_days": [],
                "backlog_reorder": [],
                "pattern_observations": [],
                "items_unblocked": [],
                "items_newly_blocked": [],
                "_raw": raw_text,
                "_parse_error": True
            }

    def _save_analysis(self, result: dict, state: dict, trigger_type: str) -> int:
        """Save analysis results to backlog_analysis table."""
        conn = self._get_conn()
        
        bills_7 = state.get('bills_due_7_days', [])
        bills_total = sum(b.get('expected_amount', 0) or 0 for b in bills_7)
        
        routines = state.get('routines_today', [])
        routines_due = len(routines)
        routines_done = sum(1 for r in routines if r.get('completion_status') == 'done')
        
        backlog = state.get('backlog', [])
        blocked = sum(1 for b in backlog if b.get('blocked_by'))
        
        transfer_recs = result.get('transfer_recommendations', [])

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO backlog_analysis (
                    trigger_type, summary, recommendations, flagged_items,
                    routines_due, routines_completed, 
                    calendar_events_today, bills_due_7_days, bills_total_due_7_days,
                    transfer_recommendations,
                    total_open_items, items_unblocked, items_blocked,
                    raw_model_response, model_used
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s,
                    %s, %s, %s,
                    %s, %s
                ) RETURNING id
            """, (
                trigger_type,
                result.get('briefing', ''),
                json.dumps(result.get('priorities_today', [])),
                result.get('items_unblocked', []),
                routines_due,
                routines_done,
                len(state.get('calendar_upcoming', [])),
                len(bills_7),
                bills_total,
                json.dumps(transfer_recs) if transfer_recs else None,
                len(backlog),
                len(result.get('items_unblocked', [])),
                blocked,
                result.get('_raw', ''),
                ANALYST_MODEL
            ))
            analysis_id = cur.fetchone()[0]
        
        conn.commit()
        return analysis_id

    def _apply_reorders(self, result: dict):
        """Apply any backlog reordering the analyst recommends."""
        reorders = result.get('backlog_reorder', [])
        if not reorders:
            return

        conn = self._get_conn()
        with conn.cursor() as cur:
            for reorder in reorders:
                item_id = reorder.get('item_id')
                new_priority = reorder.get('new_priority')
                reason = reorder.get('reason', '')
                if item_id and new_priority:
                    cur.execute("""
                        UPDATE idea_backlog 
                        SET priority_order = %s, 
                            analyst_notes = %s,
                            last_analyzed = NOW()
                        WHERE id = %s AND status NOT IN ('done', 'cancelled')
                    """, (new_priority, reason, item_id))
        conn.commit()

    async def run_analysis(self, trigger_type: str = 'morning') -> dict:
        """
        Run the full analysis pipeline.
        
        Args:
            trigger_type: 'morning', 'post_patch', 'on_demand', or 'evening'
            
        Returns:
            dict with 'briefing' (text), 'analysis_id' (int), and full result
        """
        logger.info(f"🧠 Backlog analyst running ({trigger_type})...")
        
        # 1. Gather state
        state = self._gather_state()
        logger.info(
            f"  State: {len(state['backlog'])} backlog items, "
            f"{len(state['routines_today'])} routines, "
            f"{len(state['bills_due_7_days'])} bills due 7 days, "
            f"{len(state['accounts'])} accounts"
        )
        
        # 2. Build prompt
        prompt = self._build_prompt(state, trigger_type)
        
        # 3. Call model
        result = await self._call_model(prompt)
        
        # 4. Save analysis
        analysis_id = self._save_analysis(result, state, trigger_type)
        logger.info(f"  Analysis saved: id={analysis_id}")
        
        # 5. Apply reorders (if any)
        if not result.get('_parse_error'):
            self._apply_reorders(result)
        
        # 6. Return
        result['analysis_id'] = analysis_id
        return result

    def get_latest_briefing(self) -> Optional[str]:
        """Get the most recent morning briefing text."""
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT summary FROM backlog_analysis
                WHERE trigger_type = 'morning'
                ORDER BY created_at DESC LIMIT 1
            """)
            row = cur.fetchone()
            return row[0] if row else None

    def get_transfer_recommendations(self) -> list:
        """Get the most recent transfer recommendations."""
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT transfer_recommendations FROM backlog_analysis
                WHERE transfer_recommendations IS NOT NULL
                ORDER BY created_at DESC LIMIT 1
            """)
            row = cur.fetchone()
            if row and row[0]:
                return json.loads(row[0]) if isinstance(row[0], str) else row[0]
            return []

    def close(self):
        """Close database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()


# CLI entry point for testing
if __name__ == "__main__":
    import sys
    
    trigger = sys.argv[1] if len(sys.argv) > 1 else 'on_demand'
    analyst = BacklogAnalyst()
    
    result = asyncio.run(analyst.run_analysis(trigger))
    
    print("\n" + "=" * 60)
    print("BRIEFING:")
    print("=" * 60)
    print(result.get('briefing', 'No briefing generated'))
    
    print("\n" + "=" * 60)
    print("PRIORITIES:")
    print("=" * 60)
    for p in result.get('priorities_today', []):
        print(f"  • {p}")
    
    if result.get('urgent_flags'):
        print("\n⚠️  URGENT:")
        for f in result['urgent_flags']:
            print(f"  🔴 {f}")
    
    if result.get('transfer_recommendations'):
        print("\n💰 TRANSFERS:")
        for t in result['transfer_recommendations']:
            print(f"  {t['from_account']} → {t['to_account']}: ${t['amount']} ({t['reason']})")
    
    analyst.close()

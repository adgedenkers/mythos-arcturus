"""
Analyst Handler — Telegram commands for on-demand backlog analysis.

Commands:
    /briefing       — Run analysis now, send briefing
    /priorities     — Show current top priorities
    /transfers      — Show transfer recommendations
    /analyze        — Alias for /briefing
    /reprioritize   — Run analysis with focus on reordering
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def cmd_briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run on-demand analysis and send briefing."""
    await update.message.reply_text("🔮 Running analysis... (this takes ~30s with the 32b model)")
    
    try:
        from core.backlog_analyst import BacklogAnalyst
        analyst = BacklogAnalyst()
        result = await analyst.run_analysis('on_demand')
        analyst.close()
        
        briefing = result.get('briefing', 'Analysis ran but no briefing generated.')
        
        msg_parts = [f"🔮 *On-Demand Analysis*\n"]
        msg_parts.append(briefing)
        
        urgent = result.get('urgent_flags', [])
        if urgent:
            msg_parts.append("\n\n⚠️ *Urgent:*")
            for flag in urgent:
                msg_parts.append(f"  🔴 {flag}")
        
        transfers = result.get('transfer_recommendations', [])
        if transfers:
            msg_parts.append("\n\n💰 *Transfers:*")
            for t in transfers:
                msg_parts.append(
                    f"  {t['from_account']} → {t['to_account']}: "
                    f"${t['amount']:,.2f} — {t['reason']}"
                )
        
        priorities = result.get('priorities_today', [])
        if priorities:
            msg_parts.append("\n\n📋 *Priorities:*")
            for i, p in enumerate(priorities, 1):
                msg_parts.append(f"  {i}. {p}")

        patterns = result.get('pattern_observations', [])
        if patterns:
            msg_parts.append("\n\n🔍 *Patterns:*")
            for p in patterns:
                msg_parts.append(f"  • {p}")

        await update.message.reply_text(
            "\n".join(msg_parts),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Briefing command failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Analysis failed: {str(e)[:200]}")


async def cmd_priorities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current top priorities from latest analysis."""
    try:
        import psycopg2
        import psycopg2.extras
        import json
        
        conn = psycopg2.connect(dbname='mythos', user='postgres', host='localhost')
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Get latest analysis
            cur.execute("""
                SELECT summary, recommendations, created_at, trigger_type
                FROM backlog_analysis
                ORDER BY created_at DESC LIMIT 1
            """)
            analysis = cur.fetchone()
            
            # Get top backlog items
            cur.execute("""
                SELECT id, title, priority_order, status, estimated_effort, analyst_notes
                FROM idea_backlog
                WHERE status NOT IN ('done', 'cancelled')
                ORDER BY priority_order NULLS LAST
                LIMIT 10
            """)
            items = cur.fetchall()
        conn.close()
        
        msg_parts = ["📋 *Current Priorities*\n"]
        
        if analysis:
            age = "today" if analysis['created_at'].date() == __import__('datetime').date.today() else analysis['created_at'].strftime('%b %d')
            msg_parts.append(f"_Last analysis: {age} ({analysis['trigger_type']})_\n")
        
        for item in items:
            priority = item.get('priority_order', '?')
            effort = item.get('estimated_effort', '')
            effort_icon = {'small': '🟢', 'medium': '🟡', 'large': '🔴'}.get(effort, '⚪')
            status_icon = '🔥' if item['status'] == 'active' else '⬜'
            notes = f"\n    _{item['analyst_notes']}_" if item.get('analyst_notes') else ""
            msg_parts.append(f"{status_icon} #{priority} {item['title']} {effort_icon}{notes}")
        
        await update.message.reply_text("\n".join(msg_parts), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Priorities command failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Failed: {str(e)[:200]}")


async def cmd_transfers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show latest transfer recommendations."""
    try:
        from core.backlog_analyst import BacklogAnalyst
        analyst = BacklogAnalyst()
        transfers = analyst.get_transfer_recommendations()
        analyst.close()
        
        if not transfers:
            await update.message.reply_text("✅ No transfer recommendations — accounts look balanced.")
            return
        
        msg_parts = ["💰 *Transfer Recommendations*\n"]
        for t in transfers:
            msg_parts.append(
                f"  {t['from_account']} → {t['to_account']}: "
                f"${t['amount']:,.2f}\n  _{t['reason']}_\n"
            )
        
        await update.message.reply_text("\n".join(msg_parts), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Transfers command failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Failed: {str(e)[:200]}")

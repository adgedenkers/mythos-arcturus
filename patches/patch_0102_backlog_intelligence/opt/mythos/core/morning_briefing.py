"""
Morning Briefing Scheduler

Integrates with the Telegram bot to run the backlog analyst
on schedule and send briefings.

Triggers:
  - 3:00 AM daily: Full morning analysis + Telegram briefing
  - Post-patch: Called by patch monitor (DB update only)
  - On-demand: Called by Iris chat handler

Usage in bot startup:
    from core.morning_briefing import MorningBriefing
    briefing = MorningBriefing(bot_app)
    briefing.start()
"""

import logging
import asyncio
from datetime import time, datetime, timedelta
from telegram.ext import Application

logger = logging.getLogger(__name__)

# Adge's Telegram chat ID
ADGE_CHAT_ID = 5550729358

# Seraphe's Telegram chat ID
SERAPHE_CHAT_ID = 8069190169

# Morning briefing time (3:00 AM EST)
BRIEFING_HOUR = 3
BRIEFING_MINUTE = 0

# Evening review time (9:00 PM EST)
EVENING_HOUR = 21
EVENING_MINUTE = 0

# Quiet hours — no nudges between these times
QUIET_START = 22  # 10 PM
QUIET_END = 3     # 3 AM (briefing is the exception)


class MorningBriefing:
    """Scheduled morning briefing via Telegram."""

    def __init__(self, app: Application):
        self.app = app
        self._analyst = None
        self._morning_task = None
        self._evening_task = None

    def _get_analyst(self):
        """Lazy-load the analyst to avoid circular imports."""
        if self._analyst is None:
            from core.backlog_analyst import BacklogAnalyst
            self._analyst = BacklogAnalyst()
        return self._analyst

    async def send_morning_briefing(self):
        """Run the morning analysis and send to Telegram."""
        try:
            logger.info("🌅 Running morning briefing...")
            analyst = self._get_analyst()
            result = await analyst.run_analysis('morning')
            
            briefing = result.get('briefing', 'Morning analysis ran but produced no briefing.')
            
            # Build the message
            msg_parts = [f"🌅 *Morning Briefing*\n"]
            msg_parts.append(briefing)
            
            # Add urgent flags
            urgent = result.get('urgent_flags', [])
            if urgent:
                msg_parts.append("\n\n⚠️ *Urgent:*")
                for flag in urgent:
                    msg_parts.append(f"  🔴 {flag}")
            
            # Add transfer recommendations
            transfers = result.get('transfer_recommendations', [])
            if transfers:
                msg_parts.append("\n\n💰 *Recommended Transfers:*")
                for t in transfers:
                    msg_parts.append(
                        f"  {t['from_account']} → {t['to_account']}: "
                        f"${t['amount']:,.2f} — {t['reason']}"
                    )
            
            # Add today's priorities
            priorities = result.get('priorities_today', [])
            if priorities:
                msg_parts.append("\n\n📋 *Today:*")
                for i, p in enumerate(priorities, 1):
                    msg_parts.append(f"  {i}. {p}")

            message = "\n".join(msg_parts)
            
            # Send to Adge
            await self.app.bot.send_message(
                chat_id=ADGE_CHAT_ID,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Morning briefing sent (analysis #{result.get('analysis_id')})")
            
        except Exception as e:
            logger.error(f"❌ Morning briefing failed: {e}", exc_info=True)
            try:
                await self.app.bot.send_message(
                    chat_id=ADGE_CHAT_ID,
                    text=f"⚠️ Morning briefing failed: {str(e)[:200]}"
                )
            except Exception:
                pass

    async def send_evening_review(self):
        """Run evening analysis — lighter, focused on accuracy tracking."""
        try:
            logger.info("🌙 Running evening review...")
            analyst = self._get_analyst()
            result = await analyst.run_analysis('evening')
            
            # Evening review is quieter — only send if there's something notable
            urgent = result.get('urgent_flags', [])
            if urgent:
                msg = "🌙 *Evening Check-in*\n\n" + result.get('briefing', '')
                await self.app.bot.send_message(
                    chat_id=ADGE_CHAT_ID,
                    text=msg,
                    parse_mode='Markdown'
                )
                logger.info("✅ Evening review sent (had urgent items)")
            else:
                logger.info("✅ Evening review complete (nothing urgent, no message sent)")
                
        except Exception as e:
            logger.error(f"❌ Evening review failed: {e}", exc_info=True)

    async def run_on_demand(self) -> str:
        """Run analysis on demand, return briefing text for Iris to relay."""
        analyst = self._get_analyst()
        result = await analyst.run_analysis('on_demand')
        return result.get('briefing', 'Analysis completed but no briefing generated.')

    async def run_post_patch(self):
        """Run after a patch installs — DB update only, no Telegram."""
        try:
            analyst = self._get_analyst()
            result = await analyst.run_analysis('post_patch')
            logger.info(f"✅ Post-patch analysis complete (#{result.get('analysis_id')})")
        except Exception as e:
            logger.error(f"❌ Post-patch analysis failed: {e}", exc_info=True)

    async def _schedule_loop(self):
        """Main scheduling loop — runs forever, triggers at configured times."""
        logger.info(
            f"📅 Briefing scheduler started. "
            f"Morning: {BRIEFING_HOUR}:{BRIEFING_MINUTE:02d}, "
            f"Evening: {EVENING_HOUR}:{EVENING_MINUTE:02d}"
        )
        
        while True:
            now = datetime.now()
            
            # Calculate next morning briefing time
            morning_target = now.replace(
                hour=BRIEFING_HOUR, minute=BRIEFING_MINUTE, second=0, microsecond=0
            )
            if now >= morning_target:
                morning_target += timedelta(days=1)
            
            # Calculate next evening review time
            evening_target = now.replace(
                hour=EVENING_HOUR, minute=EVENING_MINUTE, second=0, microsecond=0
            )
            if now >= evening_target:
                evening_target += timedelta(days=1)
            
            # Find which is sooner
            if morning_target < evening_target:
                next_target = morning_target
                next_action = 'morning'
            else:
                next_target = evening_target
                next_action = 'evening'
            
            wait_seconds = (next_target - now).total_seconds()
            logger.info(
                f"⏰ Next {next_action} briefing in "
                f"{wait_seconds/3600:.1f} hours ({next_target.strftime('%H:%M')})"
            )
            
            await asyncio.sleep(wait_seconds)
            
            if next_action == 'morning':
                await self.send_morning_briefing()
            else:
                await self.send_evening_review()

    def start(self):
        """Start the scheduling loop as a background task."""
        loop = asyncio.get_event_loop()
        self._morning_task = loop.create_task(self._schedule_loop())
        logger.info("🌅 Morning briefing scheduler initialized")

    def stop(self):
        """Stop the scheduling loop."""
        if self._morning_task:
            self._morning_task.cancel()
        if self._analyst:
            self._analyst.close()

"""
Astrology Handler for Mythos Telegram Bot

Commands:
    /chart <name>              - Show natal chart
    /chart <name> <name2>      - Bi-wheel comparison
    /planets <name>            - Just planet positions
    /houses <name>             - Just house cusps
    /aspects <name>            - Just aspects
    /synastry <name> <name2>   - Relationship aspects
    /group_planets <planet> <sign>  - Find all with planet in sign
    /group_houses <house>      - Show all placements in house
"""

import logging
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes

log = logging.getLogger(__name__)


async def handle_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show natal chart or comparison."""
    if not context.args:
        await update.message.reply_text(
            "Usage:\n"
            "/chart <name> - Show natal chart\n"
            "/chart <name1> <name2> - Compare two charts"
        )
        return
    
    from database.postgres_manager import PostgresManager
    db = PostgresManager()
    
    try:
        if len(context.args) == 1:
            # Single chart
            name = context.args[0]
            
            # Find chart
            result = db.execute_query("""
                SELECT id, entity_name, event_datetime, location_name
                FROM astro_charts
                WHERE LOWER(entity_name) LIKE LOWER(%s)
                ORDER BY created_at DESC
                LIMIT 1
            """, (f"%{name}%",))
            
            if not result:
                await update.message.reply_text(f"No chart found for '{name}'")
                return
            
            chart_id = result[0]['id']
            chart_name = result[0]['entity_name']
            
            # Get summary
            placements = db.execute_query("""
                SELECT body_name, position_display, house_number, is_retrograde, dignity
                FROM astro_placements
                WHERE chart_id = %s
                  AND body_name IN ('Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
                                    'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto',
                                    'Ascendant', 'Midheaven')
                ORDER BY 
                    CASE body_name
                        WHEN 'Sun' THEN 1
                        WHEN 'Moon' THEN 2
                        WHEN 'Mercury' THEN 3
                        WHEN 'Venus' THEN 4
                        WHEN 'Mars' THEN 5
                        WHEN 'Jupiter' THEN 6
                        WHEN 'Saturn' THEN 7
                        WHEN 'Uranus' THEN 8
                        WHEN 'Neptune' THEN 9
                        WHEN 'Pluto' THEN 10
                        WHEN 'Ascendant' THEN 98
                        WHEN 'Midheaven' THEN 99
                    END
            """, (chart_id,))
            
            # Format output
            lines = [f"🌟 NATAL CHART: {chart_name}", ""]
            
            for p in placements:
                retro = " ℞" if p['is_retrograde'] else ""
                dignity_emoji = {
                    'domicile': ' 👑',
                    'exaltation': ' ⬆️',
                    'detriment': ' ⬇️',
                    'fall': ' 💥',
                }.get(p['dignity'], '')
                
                lines.append(
                    f"{p['body_name']:12} {p['position_display']:20} "
                    f"H{p['house_number']}{retro}{dignity_emoji}"
                )
            
            await update.message.reply_text('\n'.join(lines), parse_mode=None)
        
        elif len(context.args) == 2:
            # Bi-wheel comparison
            name1, name2 = context.args
            
            # Find both charts
            chart1 = db.execute_query("""
                SELECT id, entity_name
                FROM astro_charts
                WHERE LOWER(entity_name) LIKE LOWER(%s)
                ORDER BY created_at DESC
                LIMIT 1
            """, (f"%{name1}%",))
            
            chart2 = db.execute_query("""
                SELECT id, entity_name
                FROM astro_charts
                WHERE LOWER(entity_name) LIKE LOWER(%s)
                ORDER BY created_at DESC
                LIMIT 1
            """, (f"%{name2}%",))
            
            if not chart1 or not chart2:
                await update.message.reply_text(
                    f"Could not find charts for '{name1}' and/or '{name2}'"
                )
                return
            
            chart1_id = chart1[0]['id']
            chart2_id = chart2[0]['id']
            chart1_name = chart1[0]['entity_name']
            chart2_name = chart2[0]['entity_name']
            
            # Get inner planets for both
            inner_bodies = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars']
            
            chart1_planets = db.execute_query("""
                SELECT body_name, sign, sign_degree, position_display
                FROM astro_placements
                WHERE chart_id = %s
                  AND body_name = ANY(%s)
                ORDER BY 
                    CASE body_name
                        WHEN 'Sun' THEN 1
                        WHEN 'Moon' THEN 2
                        WHEN 'Mercury' THEN 3
                        WHEN 'Venus' THEN 4
                        WHEN 'Mars' THEN 5
                    END
            """, (chart1_id, inner_bodies))
            
            chart2_planets = db.execute_query("""
                SELECT body_name, sign, sign_degree, position_display
                FROM astro_placements
                WHERE chart_id = %s
                  AND body_name = ANY(%s)
                ORDER BY 
                    CASE body_name
                        WHEN 'Sun' THEN 1
                        WHEN 'Moon' THEN 2
                        WHEN 'Mercury' THEN 3
                        WHEN 'Venus' THEN 4
                        WHEN 'Mars' THEN 5
                    END
            """, (chart2_id, inner_bodies))
            
            # Format comparison
            lines = [
                f"🌟 INNER PLANETS COMPARISON",
                f"{chart1_name} vs {chart2_name}",
                ""
            ]
            
            for p1, p2 in zip(chart1_planets, chart2_planets):
                lines.append(
                    f"{p1['body_name']:10} "
                    f"{p1['position_display']:20} | {p2['position_display']:20}"
                )
            
            await update.message.reply_text('\n'.join(lines), parse_mode=None)
    
    finally:
        db.close()


async def handle_planets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show just planet positions."""
    if not context.args:
        await update.message.reply_text("Usage: /planets <name>")
        return
    
    name = ' '.join(context.args)
    
    from database.postgres_manager import PostgresManager
    db = PostgresManager()
    
    try:
        result = db.execute_query("""
            SELECT id FROM astro_charts
            WHERE LOWER(entity_name) LIKE LOWER(%s)
            ORDER BY created_at DESC
            LIMIT 1
        """, (f"%{name}%",))
        
        if not result:
            await update.message.reply_text(f"No chart found for '{name}'")
            return
        
        chart_id = result[0]['id']
        
        planets = db.execute_query("""
            SELECT body_name, position_display, is_retrograde
            FROM astro_placements
            WHERE chart_id = %s
              AND body_type = 'planet'
            ORDER BY 
                CASE body_name
                    WHEN 'Sun' THEN 1
                    WHEN 'Moon' THEN 2
                    WHEN 'Mercury' THEN 3
                    WHEN 'Venus' THEN 4
                    WHEN 'Mars' THEN 5
                    WHEN 'Jupiter' THEN 6
                    WHEN 'Saturn' THEN 7
                    WHEN 'Uranus' THEN 8
                    WHEN 'Neptune' THEN 9
                    WHEN 'Pluto' THEN 10
                END
        """, (chart_id,))
        
        lines = [f"🪐 PLANETS: {name}", ""]
        
        for p in planets:
            retro = " ℞" if p['is_retrograde'] else ""
            lines.append(f"{p['body_name']:10} {p['position_display']}{retro}")
        
        await update.message.reply_text('\n'.join(lines), parse_mode=None)
    
    finally:
        db.close()


async def handle_houses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show house cusps."""
    if not context.args:
        await update.message.reply_text("Usage: /houses <name>")
        return
    
    name = ' '.join(context.args)
    
    from database.postgres_manager import PostgresManager
    db = PostgresManager()
    
    try:
        result = db.execute_query("""
            SELECT id FROM astro_charts
            WHERE LOWER(entity_name) LIKE LOWER(%s)
            ORDER BY created_at DESC
            LIMIT 1
        """, (f"%{name}%",))
        
        if not result:
            await update.message.reply_text(f"No chart found for '{name}'")
            return
        
        chart_id = result[0]['id']
        
        cusps = db.execute_query("""
            SELECT house_number, position_display
            FROM astro_house_cusps
            WHERE chart_id = %s
            ORDER BY house_number
        """, (chart_id,))
        
        lines = [f"🏠 HOUSE CUSPS: {name}", ""]
        
        for c in cusps:
            lines.append(f"House {c['house_number']:2}  {c['position_display']}")
        
        await update.message.reply_text('\n'.join(lines), parse_mode=None)
    
    finally:
        db.close()


async def handle_aspects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show natal aspects."""
    if not context.args:
        await update.message.reply_text("Usage: /aspects <name>")
        return
    
    name = ' '.join(context.args)
    
    from database.postgres_manager import PostgresManager
    db = PostgresManager()
    
    try:
        result = db.execute_query("""
            SELECT id FROM astro_charts
            WHERE LOWER(entity_name) LIKE LOWER(%s)
            ORDER BY created_at DESC
            LIMIT 1
        """, (f"%{name}%",))
        
        if not result:
            await update.message.reply_text(f"No chart found for '{name}'")
            return
        
        chart_id = result[0]['id']
        
        aspects = db.execute_query("""
            SELECT body1_name, body2_name, aspect_type, orb
            FROM astro_aspects
            WHERE chart_id = %s
              AND is_major = TRUE
            ORDER BY orb
            LIMIT 20
        """, (chart_id,))
        
        if not aspects:
            await update.message.reply_text(f"No aspects found for {name}")
            return
        
        lines = [f"✨ MAJOR ASPECTS: {name}", ""]
        
        aspect_emoji = {
            'Conjunction': '☌',
            'Opposition': '☍',
            'Trine': '△',
            'Square': '□',
            'Sextile': '⚹',
        }
        
        for a in aspects:
            emoji = aspect_emoji.get(a['aspect_type'], '•')
            lines.append(
                f"{a['body1_name']:10} {emoji} {a['body2_name']:10} "
                f"({a['orb']:.1f}°)"
            )
        
        await update.message.reply_text('\n'.join(lines), parse_mode=None)
    
    finally:
        db.close()


async def handle_group_planets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Find all people with planet in sign."""
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /group_planets <planet> <sign>\n"
            "Example: /group_planets Mars Aries"
        )
        return
    
    planet = context.args[0]
    sign = ' '.join(context.args[1:])
    
    from database.postgres_manager import PostgresManager
    db = PostgresManager()
    
    try:
        results = db.execute_query("""
            SELECT 
                c.entity_name,
                p.position_display,
                p.house_number,
                p.is_retrograde
            FROM astro_charts c
            JOIN astro_placements p ON c.id = p.chart_id
            WHERE LOWER(p.body_name) = LOWER(%s)
              AND LOWER(p.sign) = LOWER(%s)
            ORDER BY c.entity_name
        """, (planet, sign))
        
        if not results:
            await update.message.reply_text(
                f"No charts found with {planet} in {sign}"
            )
            return
        
        lines = [f"🔍 {planet} in {sign}", ""]
        
        for r in results:
            retro = " ℞" if r['is_retrograde'] else ""
            lines.append(
                f"{r['entity_name']:15} {r['position_display']:20} "
                f"H{r['house_number']}{retro}"
            )
        
        await update.message.reply_text('\n'.join(lines), parse_mode=None)
    
    finally:
        db.close()


def register_handlers(application):
    """Register astrology command handlers."""
    from telegram.ext import CommandHandler
    
    application.add_handler(CommandHandler("chart", handle_chart))
    application.add_handler(CommandHandler("planets", handle_planets))
    application.add_handler(CommandHandler("houses", handle_houses))
    application.add_handler(CommandHandler("aspects", handle_aspects))
    application.add_handler(CommandHandler("group_planets", handle_group_planets))
    
    log.info("Astrology handlers registered")

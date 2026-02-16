"""
Astrology Handler for Mythos Telegram Bot
"""

import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes

load_dotenv('/opt/mythos/.env')

log = logging.getLogger(__name__)


def get_db_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
    )


def execute_query(conn, query, params=None):
    """Execute query and return results."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params or ())
        try:
            return cur.fetchall()
        except:
            return []


async def handle_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show natal chart or comparison."""
    if not context.args:
        await update.message.reply_text(
            "Usage:\n"
            "/chart <name> - Show natal chart\n"
            "/chart <name1> <name2> - Compare two charts"
        )
        return
    
    conn = get_db_connection()
    
    try:
        if len(context.args) == 1:
            # Single chart
            name = context.args[0]
            
            # Find chart
            result = execute_query(conn, """
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
            placements = execute_query(conn, """
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
            
            # Format as aligned text
            output = f"🌟 <b>NATAL CHART: {chart_name}</b>\n\n"
            output += "<pre>"
            output += "Planet      Position               House Notes\n"
            output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            for p in placements:
                planet = p['body_name'].ljust(11)
                position = p['position_display'].ljust(22)
                house = f"H{p['house_number']:>2}" if p['house_number'] else "   "
                
                notes = []
                if p['is_retrograde']:
                    notes.append("R")
                if p['dignity'] == 'domicile':
                    notes.append("Dom")
                elif p['dignity'] == 'exaltation':
                    notes.append("Exa")
                elif p['dignity'] == 'detriment':
                    notes.append("Det")
                elif p['dignity'] == 'fall':
                    notes.append("Fal")
                
                note_str = " ".join(notes) if notes else ""
                
                output += f"{planet} {position} {house}  {note_str}\n"
            
            output += "</pre>"
            
            await update.message.reply_text(output, parse_mode='HTML')
        
        elif len(context.args) == 2:
            # Bi-wheel comparison
            name1, name2 = context.args
            
            # Find both charts
            chart1 = execute_query(conn, """
                SELECT id, entity_name
                FROM astro_charts
                WHERE LOWER(entity_name) LIKE LOWER(%s)
                ORDER BY created_at DESC
                LIMIT 1
            """, (f"%{name1}%",))
            
            chart2 = execute_query(conn, """
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
            
            # Get all major placements for both
            bodies_to_compare = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
                                 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto',
                                 'North Node', 'Chiron', 'Ascendant', 'Midheaven']
            
            chart1_planets = execute_query(conn, """
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
                        WHEN 'Jupiter' THEN 6
                        WHEN 'Saturn' THEN 7
                        WHEN 'Uranus' THEN 8
                        WHEN 'Neptune' THEN 9
                        WHEN 'Pluto' THEN 10
                        WHEN 'North Node' THEN 11
                        WHEN 'Chiron' THEN 12
                        WHEN 'Ascendant' THEN 98
                        WHEN 'Midheaven' THEN 99
                    END
            """, (chart1_id, bodies_to_compare))
            
            chart2_planets = execute_query(conn, """
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
                        WHEN 'Jupiter' THEN 6
                        WHEN 'Saturn' THEN 7
                        WHEN 'Uranus' THEN 8
                        WHEN 'Neptune' THEN 9
                        WHEN 'Pluto' THEN 10
                        WHEN 'North Node' THEN 11
                        WHEN 'Chiron' THEN 12
                        WHEN 'Ascendant' THEN 98
                        WHEN 'Midheaven' THEN 99
                    END
            """, (chart2_id, bodies_to_compare))
            
            # Format comparison
            output = f"🌟 <b>COMPARISON</b>\n"
            output += f"<b>{chart1_name}</b> vs <b>{chart2_name}</b>\n\n"
            output += "<pre>"
            output += f"Planet    {chart1_name[:10].ljust(22)} {chart2_name[:10].ljust(22)}\n"
            output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            for p1, p2 in zip(chart1_planets, chart2_planets):
                planet = p1['body_name'].ljust(9)
                pos1 = p1['position_display'].ljust(22)
                pos2 = p2['position_display'].ljust(22)
                output += f"{planet} {pos1} {pos2}\n"
            
            output += "</pre>"
            
            await update.message.reply_text(output, parse_mode='HTML')
    
    finally:
        conn.close()


async def handle_planets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show just planet positions."""
    if not context.args:
        await update.message.reply_text("Usage: /planets <name>")
        return
    
    name = ' '.join(context.args)
    
    conn = get_db_connection()
    
    try:
        result = execute_query(conn, """
            SELECT id FROM astro_charts
            WHERE LOWER(entity_name) LIKE LOWER(%s)
            ORDER BY created_at DESC
            LIMIT 1
        """, (f"%{name}%",))
        
        if not result:
            await update.message.reply_text(f"No chart found for '{name}'")
            return
        
        chart_id = result[0]['id']
        
        planets = execute_query(conn, """
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
        
        output = f"🪐 <b>PLANETS: {name}</b>\n\n<pre>"
        output += "Planet      Position               R\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        for p in planets:
            planet = p['body_name'].ljust(11)
            position = p['position_display'].ljust(22)
            retro = "R" if p['is_retrograde'] else " "
            output += f"{planet} {position} {retro}\n"
        
        output += "</pre>"
        
        await update.message.reply_text(output, parse_mode='HTML')
    
    finally:
        conn.close()


async def handle_houses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show house cusps."""
    if not context.args:
        await update.message.reply_text("Usage: /houses <name>")
        return
    
    name = ' '.join(context.args)
    
    conn = get_db_connection()
    
    try:
        result = execute_query(conn, """
            SELECT id FROM astro_charts
            WHERE LOWER(entity_name) LIKE LOWER(%s)
            ORDER BY created_at DESC
            LIMIT 1
        """, (f"%{name}%",))
        
        if not result:
            await update.message.reply_text(f"No chart found for '{name}'")
            return
        
        chart_id = result[0]['id']
        
        cusps = execute_query(conn, """
            SELECT house_number, position_display
            FROM astro_house_cusps
            WHERE chart_id = %s
            ORDER BY house_number
        """, (chart_id,))
        
        output = f"🏠 <b>HOUSE CUSPS: {name}</b>\n\n<pre>"
        output += "House Position\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        for c in cusps:
            output += f"H {c['house_number']:>2}  {c['position_display']}\n"
        
        output += "</pre>"
        
        await update.message.reply_text(output, parse_mode='HTML')
    
    finally:
        conn.close()


async def handle_aspects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show natal aspects."""
    if not context.args:
        await update.message.reply_text("Usage: /aspects <name>")
        return
    
    name = ' '.join(context.args)
    
    conn = get_db_connection()
    
    try:
        result = execute_query(conn, """
            SELECT id FROM astro_charts
            WHERE LOWER(entity_name) LIKE LOWER(%s)
            ORDER BY created_at DESC
            LIMIT 1
        """, (f"%{name}%",))
        
        if not result:
            await update.message.reply_text(f"No chart found for '{name}'")
            return
        
        chart_id = result[0]['id']
        
        aspects = execute_query(conn, """
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
        
        output = f"✨ <b>MAJOR ASPECTS: {name}</b>\n\n<pre>"
        output += "Body 1       Aspect        Body 2         Orb\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        for a in aspects:
            body1 = a['body1_name'].ljust(12)
            aspect = a['aspect_type'].ljust(13)
            body2 = a['body2_name'].ljust(14)
            orb = f"{a['orb']:>5.2f}°"
            output += f"{body1} {aspect} {body2} {orb}\n"
        
        output += "</pre>"
        
        await update.message.reply_text(output, parse_mode='HTML')
    
    finally:
        conn.close()


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
    
    conn = get_db_connection()
    
    try:
        results = execute_query(conn, """
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
        
        output = f"🔍 <b>{planet} in {sign}</b>\n\n<pre>"
        output += "Name            Position               House R\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        for r in results:
            name = r['entity_name'].ljust(15)
            position = r['position_display'].ljust(22)
            house = f"H{r['house_number']:>2}" if r['house_number'] else "   "
            retro = "R" if r['is_retrograde'] else " "
            output += f"{name} {position} {house} {retro}\n"
        
        output += "</pre>"
        
        await update.message.reply_text(output, parse_mode='HTML')
    
    finally:
        conn.close()


def register_handlers(application):
    """Register astrology command handlers."""
    from telegram.ext import CommandHandler
    
    application.add_handler(CommandHandler("chart", handle_chart))
    application.add_handler(CommandHandler("planets", handle_planets))
    application.add_handler(CommandHandler("houses", handle_houses))
    application.add_handler(CommandHandler("aspects", handle_aspects))
    application.add_handler(CommandHandler("group_planets", handle_group_planets))
    
    log.info("Astrology handlers registered")

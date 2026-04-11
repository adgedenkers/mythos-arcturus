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
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Exception as e:
        if conn:
            conn.close()
        raise e

class QueryNatalChartSkill(SkillBase):
    name = 'query_natal_chart'
    triggers = [
        'natal chart', 'birth chart', 'placements', 'what sign',
        'rising sign', 'moon sign', 'sun sign', 'chart for',
        'astrology chart', 'where is my'
    ]
    cache_ttl = 3600

    NAME_MAP = {
        'adge': 'Adge',
        'adriaan': 'Adge',
        'rebecca': 'Becky',
        'becky': 'Becky',
        'seraphe': 'Becky',
        'fitz': 'Fitz',
        'brandi': 'Brandi Carlile',
        'riley': 'Riley Green'
    }

    def execute(self, request: SkillRequest) -> SkillResponse:
        try:
            name = self._resolve_name(request.message)
            chart_data = self._query_chart(name)
            if not chart_data:
                available_names = ['Adge', 'Becky', 'Fitz', 'Brandi Carlile', 'Riley Green']
                return SkillResponse(
                    text=f"No natal chart found for {name}. Available: {', '.join(available_names)}."
                )
            
            placements = self._query_placements(chart_data['chart_id'])
            formatted = self._format(chart_data, placements)
            summary = self._build_summary(chart_data, placements)
            return SkillResponse(
                skill_name=self.name,
                data=formatted,
                summary=summary,
                confidence=0.95,
                sources=['mythos.astro_natal_charts', 'mythos.astro_chart_objects']
            )
        except Exception as e:
            logging.error(f"Error in QueryNatalChartSkill.execute: {e}")
            raise e

    def _resolve_name(self, name: str) -> str:
        name = name.lower().strip()
        for key, value in self.NAME_MAP.items():
            if key in name:
                return value
        return 'Adge'

    def _query_chart(self, name: str) -> dict:
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT chart_id, name, birth_date, birth_time, birth_place, house_system, zodiac_type FROM astro_natal_charts WHERE name = %s",
                    (name,)
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        finally:
            if conn:
                conn.close()

    def _query_placements(self, chart_id: int) -> list:
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT object_name, sign, deg_min, full_position, is_retrograde, house FROM astro_chart_objects WHERE chart_id = %s ORDER BY CASE object_name WHEN 'Sun' THEN 1 WHEN 'Moon' THEN 2 WHEN 'Mercury' THEN 3 WHEN 'Venus' THEN 4 WHEN 'Mars' THEN 5 WHEN 'Jupiter' THEN 6 WHEN 'Saturn' THEN 7 ELSE 8 END",
                    (chart_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
        finally:
            if conn:
                conn.close()

    def _format(self, chart_data: dict, placements: list) -> str:
        summary = self._build_summary(chart_data, placements)
        placements_str = "\n".join([
            f"  {obj['object_name']}: {obj['sign']} {obj['deg_min']} in House {obj['house']}"
            for obj in placements
        ])
        return f"{summary}\n\nPlacements:\n{placements_str}"

    def _build_summary(self, chart_data: dict, placements: list) -> str:
        # Filter for major planets
        major_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        chart_placements = [p for p in placements if p['object_name'] in major_planets]
        
        # Build summary string
        summary_parts = []
        for obj in chart_placements:
            retro_symbol = " R" if obj['is_retrograde'] else ""
            summary_parts.append(f"{obj['object_name']} in {obj['sign']} ({obj['house']}){retro_symbol}")
        
        if not summary_parts:
            return "No major planet placements found."
        
        return (f"{chart_data['name']} chart ({chart_data['zodiac_type']}, {chart_data['house_system']}): " +
                " | ".join(summary_parts))
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
        pass

    def _resolve_name(self, name: str) -> str:
        pass

    def _query_chart(self, name: str) -> dict:
        pass

    def _query_placements(self, chart_id: int) -> list:
        pass

    def _format(self, chart_data: dict, placements: list) -> str:
        pass

    def _build_summary(self, chart_data: dict, placements: list) -> str:
        pass
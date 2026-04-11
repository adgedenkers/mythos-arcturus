#!/usr/bin/env python3
"""
People Lookup Skill
===================

Searches the people registry in PostgreSQL by name, nickname (known_as),
or ID. Returns matching person records with birth data and notes.
Used when Iris needs to identify someone, check birth details for astrology,
or answer "who is X?" questions.
"""
import os
import logging
from typing import Any, Dict

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

from engine.base import SkillBase, SkillRequest, SkillResponse

logger = logging.getLogger(__name__)


def _get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor,
    )


class PeopleLookupSkill(SkillBase):
    name = "people_lookup"
    version = "1.0"
    category = "data"
    description = "Search the people registry by name, nickname, or ID"
    triggers = [
        "who is", "find person", "look up person", "people",
        "person", "lookup", "born", "birthday", "birth data",
        "birth chart for", "date of birth", "known as",
        "find someone", "person named",
    ]
    cache_ttl = 600  # 10 minutes — people data rarely changes

    async def execute(self, request: SkillRequest) -> SkillResponse:
        conn = None
        try:
            conn = _get_conn()
            cur = conn.cursor()

            msg = request.message.lower()

            # Try to extract a search term from the message
            search_term = self._extract_search_term(msg)

            if not search_term:
                # Return all people count as a fallback
                cur.execute("SELECT COUNT(*) as total FROM people")
                total = cur.fetchone()['total']
                cur.close()
                return SkillResponse(
                    skill_name=self.name,
                    data={"total_people": total},
                    summary=f"People registry has {total} entries. Ask about a specific person by name.",
                    confidence=0.5,
                    sources=["mythos.people"],
                )

            # Search by name or known_as
            cur.execute("""
                SELECT id, prefix, first_name, middle_name, last_name, suffix,
                       known_as, date_of_birth, time_of_birth,
                       birth_city, birth_state, birth_country,
                       date_of_death, notes, canonical_id
                FROM people
                WHERE LOWER(first_name) LIKE %s
                   OR LOWER(last_name) LIKE %s
                   OR LOWER(known_as) LIKE %s
                   OR LOWER(first_name || ' ' || last_name) LIKE %s
                ORDER BY last_name, first_name
                LIMIT 10
            """, (f"%{search_term}%",) * 4)

            rows = cur.fetchall()
            cur.close()

            if not rows:
                return SkillResponse(
                    skill_name=self.name,
                    data={"matches": [], "search_term": search_term},
                    summary=f"No people found matching '{search_term}'.",
                    confidence=0.8,
                    sources=["mythos.people"],
                )

            # Build structured data
            people = []
            summary_parts = []

            for row in rows:
                person = {
                    "id": row["id"],
                    "name": self._format_name(row),
                    "known_as": row["known_as"],
                    "date_of_birth": str(row["date_of_birth"]) if row["date_of_birth"] else None,
                    "time_of_birth": str(row["time_of_birth"]) if row["time_of_birth"] else None,
                    "birth_location": self._format_birth_location(row),
                    "date_of_death": str(row["date_of_death"]) if row["date_of_death"] else None,
                    "notes": row["notes"],
                    "canonical_id": row["canonical_id"],
                }
                people.append(person)

                # Build summary line
                name_str = person["name"]
                if row["known_as"]:
                    name_str += f" (aka {row['known_as']})"
                if row["date_of_birth"]:
                    name_str += f", born {row['date_of_birth']}"
                    if person["birth_location"]:
                        name_str += f" in {person['birth_location']}"
                summary_parts.append(name_str)

            match_word = "person" if len(people) == 1 else "people"
            summary = (
                f"Found {len(people)} {match_word} matching '{search_term}': "
                + "; ".join(summary_parts)
            )

            return SkillResponse(
                skill_name=self.name,
                data={"matches": people, "search_term": search_term},
                summary=summary,
                confidence=0.95,
                sources=["mythos.people"],
            )

        except Exception as e:
            logger.error(f"People lookup failed: {e}", exc_info=True)
            return SkillResponse(skill_name=self.name, error=str(e))
        finally:
            if conn:
                conn.close()

    def _extract_search_term(self, msg: str) -> str:
        """Extract the person's name or search term from the message."""
        # Remove common preamble phrases
        removals = [
            "who is", "find person", "look up person", "look up",
            "find someone named", "person named", "find",
            "tell me about", "search for", "lookup",
            "birth data for", "birth chart for", "date of birth for",
        ]
        cleaned = msg
        for phrase in removals:
            cleaned = cleaned.replace(phrase, "")
        cleaned = cleaned.strip().strip("?").strip()
        return cleaned if len(cleaned) >= 2 else ""

    def _format_name(self, row: dict) -> str:
        """Build a display name from name parts."""
        parts = []
        if row.get("prefix"):
            parts.append(row["prefix"])
        parts.append(row["first_name"])
        if row.get("middle_name"):
            parts.append(row["middle_name"])
        parts.append(row["last_name"])
        if row.get("suffix"):
            parts.append(row["suffix"])
        return " ".join(parts)

    def _format_birth_location(self, row: dict) -> str:
        """Build a birth location string."""
        parts = []
        if row.get("birth_city"):
            parts.append(row["birth_city"])
        if row.get("birth_state"):
            parts.append(row["birth_state"])
        if row.get("birth_country") and row["birth_country"] != "US":
            parts.append(row["birth_country"])
        return ", ".join(parts)

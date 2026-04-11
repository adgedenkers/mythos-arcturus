#!/usr/bin/env python3
"""
People Lookup
=============

Searches the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match).
Returns matching records with birth data. If no search term can be extracted, returns the total count
of people in the registry.
"""
import os
import logging
import re
from typing import Dict, List, Optional, Any

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
    description = "Searches the Mythos people table by name or alias, returning birth data"
    triggers = [
        "who is",
        "find person",
        "people",
        "person",
        "lookup",
        "born",
        "birthday",
        "birth data"
    ]
    cache_ttl = 600

    def _extract_search_term(self, message: str) -> Optional[str]:
        """Extract a search term from the user message."""
        # Remove common trigger phrases
        clean_message = re.sub(r'^(who is|find person|people|person|lookup|born|birthday|birth data)\s+', '', message, flags=re.IGNORECASE)
        # Remove extra whitespace
        clean_message = clean_message.strip()
        # If we have a valid term, return it
        if clean_message and len(clean_message) > 1:
            return clean_message
        return None

    def _format_name(self, person: Dict[str, Any]) -> str:
        """Format a person's name for display."""
        parts = []
        if person.get('prefix'):
            parts.append(person['prefix'])
        if person.get('first_name'):
            parts.append(person['first_name'])
        if person.get('middle_name'):
            parts.append(person['middle_name'])
        if person.get('last_name'):
            parts.append(person['last_name'])
        if person.get('suffix'):
            parts.append(person['suffix'])
        return ' '.join(parts).strip() or person.get('display_text', '')

    def _format_birth_location(self, person: Dict[str, Any]) -> str:
        """Format birth location for display."""
        location_parts = []
        if person.get('birth_city'):
            location_parts.append(person['birth_city'])
        if person.get('birth_state'):
            location_parts.append(person['birth_state'])
        if person.get('birth_country'):
            location_parts.append(person['birth_country'])
        return ', '.join(location_parts) if location_parts else 'Unknown'

    async def execute(self, request: SkillRequest) -> SkillResponse:
        try:
            conn = _get_conn()
            cur = conn.cursor()

            search_term = self._extract_search_term(request.message)
            
            if not search_term:
                # No search term found, return total count
                cur.execute("SELECT COUNT(*) as total FROM people")
                result = cur.fetchone()
                total = result['total'] if result else 0
                summary = f"There are {total} people in the registry."
                return SkillResponse(
                    skill_name=self.name,
                    data={"total_count": total},
                    summary=summary,
                    confidence=0.95,
                    sources=["mythos.people"],
                )

            # Search for matching people
            search_pattern = f"%{search_term}%"
            cur.execute("""
                SELECT 
                    id, prefix, first_name, middle_name, last_name, suffix, known_as,
                    date_of_birth, time_of_birth, birth_city, birth_state, birth_zip, 
                    birth_country, display_text
                FROM people 
                WHERE 
                    first_name ILIKE %s 
                    OR last_name ILIKE %s 
                    OR known_as ILIKE %s
                ORDER BY last_name, first_name
            """, (search_pattern, search_pattern, search_pattern))

            results = cur.fetchall()
            
            if not results:
                summary = f"No people found matching '{search_term}'."
                return SkillResponse(
                    skill_name=self.name,
                    data={"results": []},
                    summary=summary,
                    confidence=0.95,
                    sources=["mythos.people"],
                )

            formatted_results = []
            for person in results:
                formatted_person = {
                    "name": self._format_name(person),
                    "birth_date": person.get('date_of_birth'),
                    "birth_location": self._format_birth_location(person)
                }
                formatted_results.append(formatted_person)

            # Build summary
            names = [p["name"] for p in formatted_results]
            if len(names) == 1:
                summary = f"Found 1 person: {names[0]}"
            else:
                summary = f"Found {len(names)} people: " + ", ".join(names)
            
            return SkillResponse(
                skill_name=self.name,
                data={"results": formatted_results},
                summary=summary,
                confidence=0.95,
                sources=["mythos.people"],
            )

        except Exception as e:
            logger.error(f"Error in people lookup: {str(e)}")
            return SkillResponse(
                skill_name=self.name,
                data={},
                summary="An error occurred while searching for people.",
                confidence=0.0,
                sources=["mythos.people"],
                error=str(e)
            )
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()
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
from typing import Any, Dict, List

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
    description = "Searches the Mythos people table by name or alias, returning birth data for matches."
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

    async def execute(self, request: SkillRequest) -> SkillResponse:
        try:
            conn = _get_conn()
            cur = conn.cursor()

            message = request.message.lower()
            search_term = None

            # Extract search term from message
            if "who is" in message:
                search_term = message.split("who is", 1)[1].strip()
            elif "find person" in message:
                search_term = message.split("find person", 1)[1].strip()
            elif "lookup" in message:
                search_term = message.split("lookup", 1)[1].strip()
            elif "born" in message or "birthday" in message or "birth data" in message:
                # Try to extract name after these keywords
                for keyword in ["born", "birthday", "birth data"]:
                    if keyword in message:
                        parts = message.split(keyword, 1)
                        if len(parts) > 1:
                            search_term = parts[1].strip()
                            break

            # If we still don't have a search term, get total count
            if not search_term:
                cur.execute("SELECT COUNT(*) as total FROM people")
                result = cur.fetchone()
                total = result['total'] if result else 0
                summary = f"The registry contains {total} people."
                return SkillResponse(
                    skill_name=self.name,
                    data={"total_count": total},
                    summary=summary,
                    confidence=0.95,
                    sources=["mythos.people"],
                )

            # Search for people matching the term
            search_term = f"%{search_term}%"
            cur.execute("""
                SELECT 
                    id, prefix, first_name, middle_name, last_name, suffix,
                    known_as, display_text, date_of_birth, time_of_birth,
                    birth_city, birth_state, birth_zip, birth_country,
                    date_of_death, notes, canonical_id, created_at, updated_at
                FROM people
                WHERE 
                    LOWER(first_name) LIKE %s OR 
                    LOWER(last_name) LIKE %s OR 
                    LOWER(known_as) LIKE %s
                ORDER BY last_name, first_name
            """, (search_term, search_term, search_term))

            results = cur.fetchall()

            if not results:
                summary = f"No people found matching '{search_term.strip('%')}'."
                return SkillResponse(
                    skill_name=self.name,
                    data={"people": []},
                    summary=summary,
                    confidence=0.95,
                    sources=["mythos.people"],
                )

            people_data = []
            names = []

            for row in results:
                person = {
                    'id': row['id'],
                    'prefix': row['prefix'],
                    'first_name': row['first_name'],
                    'middle_name': row['middle_name'],
                    'last_name': row['last_name'],
                    'suffix': row['suffix'],
                    'known_as': row['known_as'],
                    'display_text': row['display_text'],
                    'date_of_birth': row['date_of_birth'],
                    'time_of_birth': row['time_of_birth'],
                    'birth_city': row['birth_city'],
                    'birth_state': row['birth_state'],
                    'birth_zip': row['birth_zip'],
                    'birth_country': row['birth_country'],
                    'date_of_death': row['date_of_death'],
                    'notes': row['notes'],
                    'canonical_id': row['canonical_id'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }

                # Build full name for summary
                name_parts = [person['first_name']]
                if person['middle_name']:
                    name_parts.append(person['middle_name'])
                name_parts.append(person['last_name'])
                full_name = ' '.join(name_parts)
                if person['suffix']:
                    full_name += f' {person["suffix"]}'
                if person['known_as']:
                    full_name += f" (also known as {person['known_as']})"

                names.append(full_name)
                people_data.append(person)

            # Create summary
            if len(names) == 1:
                summary = f"1 person matches: {names[0]}."
            else:
                summary = f"{len(names)} people match: {', '.join(names)}."
                
            return SkillResponse(
                skill_name=self.name,
                data={"people": people_data},
                summary=summary,
                confidence=0.95,
                sources=["mythos.people"],
            )

        except Exception as e:
            logger.error(f"Error in people lookup: {str(e)}")
            return SkillResponse(
                skill_name=self.name,
                data={"error": str(e)},
                summary="An error occurred while searching for people.",
                confidence=0.5,
                sources=["mythos.people"],
                ok=False
            )
        finally:
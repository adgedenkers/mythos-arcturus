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
    description = "Searches the Mythos people table by name or alias, returning birth data."
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
    cache_ttl = 600  # seconds

    async def execute(self, request: SkillRequest) -> SkillResponse:
        try:
            conn = _get_conn()
            cur = conn.cursor()

            message = request.message.lower()
            search_term = None

            # Extract search term from message
            if "who is" in message:
                match = re.search(r'who is\s+(.+)', message)
                if match:
                    search_term = match.group(1).strip()
            elif "find person" in message:
                match = re.search(r'find person\s+(.+)', message)
                if match:
                    search_term = match.group(1).strip()
            elif "lookup" in message:
                match = re.search(r'lookup\s+(.+)', message)
                if match:
                    search_term = match.group(1).strip()
            elif "born" in message or "birthday" in message or "birth data" in message:
                # Try to extract name from context
                words = message.split()
                for i, word in enumerate(words):
                    if word in ["born", "birthday", "birth", "data"]:
                        if i + 1 < len(words):
                            search_term = words[i + 1]
                            break

            # If no search term found, get total count
            if not search_term:
                cur.execute("SELECT COUNT(*) as total FROM people;")
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

            # Search for matching people
            search_term = search_term.replace("'", "''")  # Escape single quotes
            query = """
                SELECT 
                    id, prefix, first_name, middle_name, last_name, suffix, 
                    known_as, display_text, date_of_birth, time_of_birth, 
                    birth_city, birth_state, birth_zip, birth_country, 
                    date_of_death, notes, canonical_id, created_at, updated_at
                FROM people 
                WHERE 
                    LOWER(first_name) LIKE LOWER(%s) OR
                    LOWER(last_name) LIKE LOWER(%s) OR
                    LOWER(known_as) LIKE LOWER(%s)
                ORDER BY last_name, first_name;
            """
            cur.execute(query, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            results = cur.fetchall()

            if not results:
                summary = f"No people found matching '{search_term}'."
                return SkillResponse(
                    skill_name=self.name,
                    data={"results": []},
                    summary=summary,
                    confidence=0.85,
                    sources=["mythos.people"],
                )

            # Format results for summary
            people_list = []
            for person in results:
                name_parts = []
                if person['prefix']:
                    name_parts.append(person['prefix'])
                if person['first_name']:
                    name_parts.append(person['first_name'])
                if person['middle_name']:
                    name_parts.append(person['middle_name'])
                if person['last_name']:
                    name_parts.append(person['last_name'])
                if person['suffix']:
                    name_parts.append(person['suffix'])

                full_name = ' '.join(name_parts) if name_parts else "Unknown"

                # Build birth info
                birth_info = []
                if person['date_of_birth']:
                    birth_info.append(f"born {person['date_of_birth']}")
                if person['birth_city']:
                    birth_info.append(f"in {person['birth_city']}")
                if person['birth_state']:
                    birth_info.append(f"{person['birth_state']}")
                if person['birth_country']:
                    birth_info.append(f"{person['birth_country']}")

                birth_str = ', '.join(birth_info) if birth_info else "birth information unavailable"

                people_list.append(f"{full_name} ({birth_str})")

            summary = f"Found {len(people_list)} person{'s' if len(people_list) > 1 else ''} matching '{search_term}': " + ", ".join(people_list)

            # Prepare structured data
            data = {
                "search_term": search_term,
                "results": [
                    {
                        "id": person['id'],
                        "prefix": person['prefix'],
                        "first_name": person['first_name'],
                        "middle_name": person['middle_name'],
                        "last_name": person['last_name'],
                        "suffix": person['suffix'],
                        "known_as": person['known_as'],
                        "display_text": person['display_text'],
                        "date_of_birth": person['date_of_birth'],
                        "time_of_birth": person['time_of_birth'],
                        "birth_city": person['birth_city'],
                        "birth_state": person['birth_state'],
                        "birth_zip": person['birth_zip'],
                        "birth_country": person['birth_country'],
                        "date_of_death": person['date_of_death'],
                        "notes": person['notes'],
                        "canonical_id": person['canonical_id'],
                        "created_at": person['created_at'],
                        "updated_at": person['updated_at']
                    }
                    for person in results
                ]
            }

            return SkillResponse(
                skill_name=self.name,
                data=data,
                summary=summary,
                confidence=0.95,
                sources=["mythos.people"],
            )

        except Exception as e:
            logger.error(f"Error in people_lookup: {str(e)}")
            return SkillResponse(
                skill_name=self.name,
                data={},
                summary="An error occurred while searching for people.",
                confidence=0.0,
                sources=[],
                error=str(e)
            )
        finally:
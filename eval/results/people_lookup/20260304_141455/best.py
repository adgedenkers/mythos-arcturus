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
            search_term = f"%{search_term}%"
            cur.execute("""
                SELECT 
                    id, prefix, first_name, middle_name, last_name, suffix, 
                    known_as, display_text, date_of_birth, time_of_birth, 
                    birth_city, birth_state, birth_zip, birth_country, 
                    date_of_death, notes, canonical_id, created_at, updated_at
                FROM people 
                WHERE 
                    first_name ILIKE %s OR 
                    last_name ILIKE %s OR 
                    known_as ILIKE %s
                ORDER BY last_name, first_name;
            """, (search_term, search_term, search_term))

            results = cur.fetchall()

            if not results:
                summary = f"No people found matching '{search_term.strip('%')}'."
                return SkillResponse(
                    skill_name=self.name,
                    data={"results": []},
                    summary=summary,
                    confidence=0.8,
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

                full_name = " ".join(name_parts).strip()
                if not full_name:
                    full_name = "Unknown"

                birth_info = []
                if person['date_of_birth']:
                    birth_info.append(f"born {person['date_of_birth']}")
                if person['birth_city']:
                    birth_info.append(f"in {person['birth_city']}")
                if person['birth_state']:
                    birth_info.append(f"{person['birth_state']}")

                birth_str = ", ".join(birth_info) if birth_info else "no birth info"

                people_list.append(f"{full_name} ({birth_str})")

            summary = f"Found {len(results)} person{'s' if len(results) != 1 else ''} matching '{search_term.strip('%')}': " + ", ".join(people_list)

            # Prepare structured data
            structured_results = []
            for person in results:
                structured_results.append({
                    "id": person['id'],
                    "name": {
                        "prefix": person['prefix'],
                        "first_name": person['first_name'],
                        "middle_name": person['middle_name'],
                        "last_name": person['last_name'],
                        "suffix": person['suffix'],
                        "display_text": person['display_text'],
                        "known_as": person['known_as']
                    },
                    "birth_info": {
                        "date": person['date_of_birth'],
                        "time": person['time_of_birth'],
                        "city": person['birth_city'],
                        "state": person['birth_state'],
                        "zip": person['birth_zip'],
                        "country": person['birth_country']
                    },
                    "death_date": person['date_of_death'],
                    "notes": person['notes'],
                    "canonical_id": person['canonical_id'],
                    "created_at": person['created_at'],
                    "updated_at": person['updated_at']
                })

            return SkillResponse(
                skill_name=self.name,
                data={"results": structured_results},
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
                confidence=0.1,
                sources=["mythos.people"],
                ok=False
            )
        finally:
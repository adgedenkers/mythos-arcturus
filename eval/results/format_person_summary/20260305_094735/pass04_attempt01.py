import logging
import unicodedata
from engine.base import SkillBase, SkillRequest, SkillResponse

class FormatPersonSummarySkill(SkillBase):
    name = 'format_person_summary'
    version = '1.0'
    category = 'meta'
    description = 'Format person data into a standard readable summary'
    triggers = ['format person', 'person summary', 'who is']
    cache_ttl = 0

    async def execute(self, request) -> SkillResponse:
        # Expects request.parameters['person'] as a dict with people table fields
        try:
            person = request.parameters.get('person', {})
            if not person:
                return SkillResponse(
                    skill_name=self.name,
                    data={},
                    summary='No person data to format.',
                    confidence=0.3,
                    sources=[]
                )
            
            formatted = self._format(person)
            
            return SkillResponse(
                skill_name=self.name,
                data={
                    'formatted': formatted,
                    'person_id': person.get('id')
                },
                summary=formatted,
                confidence=0.95,
                sources=['format_person_summary']
            )
        except Exception as e:
            logging.error(f"Error in FormatPersonSummarySkill.execute: {e}")
            return SkillResponse(
                skill_name=self.name,
                data={},
                summary=f'Error formatting person data: {str(e)}',
                confidence=0.0,
                sources=[]
            )

    def _format(self, person) -> str:
        # Build: 'Name (aka Nickname), born DATE in CITY, STATE'
        parts = []
        
        # Build name from parts
        name_parts = []
        if person.get('prefix'):
            name_parts.append(person['prefix'])
        if person.get('first_name'):
            name_parts.append(person['first_name'])
        if person.get('middle_name'):
            name_parts.append(person['middle_name'])
        if person.get('last_name'):
            name_parts.append(person['last_name'])
        if person.get('suffix'):
            name_parts.append(person['suffix'])
        
        if name_parts:
            name = ' '.join(name_parts)
            if person.get('known_as'):
                name += f' (aka {person["known_as"]})'
            parts.append(name)
        
        # Add date of birth
        if person.get('date_of_birth'):
            parts.append(f'born {person["date_of_birth"]}')
        
        # Add birth location
        birth_city = person.get('birth_city')
        birth_state = person.get('birth_state')
        birth_country = person.get('birth_country')
        
        if birth_city or birth_state:
            location_parts = []
            if birth_city:
                location_parts.append(birth_city)
            if birth_state and birth_state != birth_country:
                location_parts.append(birth_state)
            if location_parts:
                parts.append('in ' + ', '.join(location_parts))
        
        # Add date of death
        if person.get('date_of_death'):
            parts.append(f'died {person["date_of_death"]}')
        
        # Add notes if less than 100 characters
        if person.get('notes') and len(person['notes']) < 100:
            parts.append(f'Notes: {person["notes"]}')
        
        result = ', '.join(parts)
        
        # Ensure ASCII only
        ascii_result = ''.join(char for char in result if ord(char) < 128)
        
        # Ensure summary is never empty
        if not ascii_result.strip():
            return 'No available information.'
            
        return ascii_result
import logging
import re
from datetime import date, timedelta
import calendar
from engine.base import SkillBase, SkillRequest, SkillResponse

class ExtractDateRangeSkill(SkillBase):
    name = 'extract_date_range'
    version = '1.0'
    category = 'meta'
    description = 'Parse natural language dates into start/end date pairs'
    triggers = ['yesterday', 'last week', 'last month', 'this week', 'this month', 'today', 'past', 'recent', 'ago', 'since', 'between', 'in january', 'in february', 'in march']
    cache_ttl = 0

    async def execute(self, request) -> SkillResponse:
        try:
            start, end, desc = self._parse_dates(request.message)
            if start is None:
                return SkillResponse(
                    skill_name=self.name,
                    data={'start_date': None, 'end_date': None, 'detected': False},
                    summary='No date reference detected in message.',
                    confidence=0.3,
                    sources=['extract_date_range']
                )
            else:
                return SkillResponse(
                    skill_name=self.name,
                    data={'start_date': str(start), 'end_date': str(end), 'description': desc, 'detected': True},
                    summary=f'Date range: {desc} ({start} to {end})',
                    confidence=0.9,
                    sources=['extract_date_range']
                )
        except Exception as e:
            logging.error(f"Error in extract_date_range skill: {e}")
            return SkillResponse(
                skill_name=self.name,
                data={'start_date': None, 'end_date': None, 'detected': False},
                summary='Error processing date range.',
                confidence=0.0,
                sources=['extract_date_range']
            )

    def _parse_dates(self, message) -> tuple:
        # Return (start_date, end_date, description)
        # Handle: today, yesterday, this week, last week, this month, last month,
        #         past N days, N days ago, specific months like 'in march'
        msg = message.lower()
        
        today = date.today()
        
        # Check for 'today'
        if 'today' in msg:
            return (today, today, 'today')
        
        # Check for 'yesterday'
        if 'yesterday' in msg:
            yesterday = today - timedelta(days=1)
            return (yesterday, yesterday, 'yesterday')
        
        # Check for 'this week'
        if 'this week' in msg:
            # Get Monday of this week
            monday = today - timedelta(days=today.weekday())
            return (monday, today, 'this week')
        
        # Check for 'last week'
        if 'last week' in msg:
            # Get Sunday of last week
            sunday = today - timedelta(days=today.weekday() + 1)
            # Get Monday of last week
            monday = sunday - timedelta(days=6)
            return (monday, sunday, 'last week')
        
        # Check for 'this month'
        if 'this month' in msg:
            # First day of this month
            first_day = date(today.year, today.month, 1)
            return (first_day, today, 'this month')
        
        # Check for 'last month'
        if 'last month' in msg:
            # First day of last month
            if today.month == 1:
                first_day = date(today.year - 1, 12, 1)
            else:
                first_day = date(today.year, today.month - 1, 1)
            
            # Last day of last month
            if today.month == 1:
                last_day = date(today.year - 1, 12, 31)
            else:
                last_day = date(today.year, today.month - 1, calendar.monthrange(today.year, today.month - 1)[1])
            
            return (first_day, last_day, 'last month')
        
        # Check for 'past N days' or 'last N days'
        past_match = re.search(r'past (\d+) days?', msg)
        last_match = re.search(r'last (\d+) days?', msg)
        if past_match or last_match:
            if past_match:
                n = int(past_match.group(1))
            else:
                n = int(last_match.group(1))
            start_date = today - timedelta(days=n)
            return (start_date, today, f'past {n} days')
        
        # Check for 'N days ago'
        ago_match = re.search(r'(\d+) days? ago', msg)
        if ago_match:
            n = int(ago_match.group(1))
            start_date = today - timedelta(days=n)
            return (start_date, start_date, f'{n} days ago')
        
        # Check for specific months
        month_names = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]
        
        for i, month_name in enumerate(month_names, 1):
            if f'in {month_name}' in msg:
                # First day of that month this year
                first_day = date(today.year, i, 1)
                # Last day of that month
                last_day = date(today.year, i, calendar.monthrange(today.year, i)[1])
                return (first_day, last_day, f'in {month_name}')
        
        # If nothing matches
        return (None, None, 'no date detected')
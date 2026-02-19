#!/usr/bin/env python3
"""
Neo4j Date Standardizer for GenPerson nodes
Target format: MM-DD-YYYY (00 for unknown month/day)
Run on Arcturus: /opt/mythos/.venv/bin/python3 fix_dates.py
"""

import re
import os
from neo4j import GraphDatabase

# --- Config ---
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASSWORD", "")

# If password not in env, try reading from .env file
if not NEO4J_PASS:
    env_path = "/opt/mythos/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("NEO4J_PASSWORD="):
                    NEO4J_PASS = line.strip().split("=", 1)[1].strip('"').strip("'")
                    break

MONTHS = {
    'jan': '01', 'january': '01', 'januari': '01',
    'feb': '02', 'february': '02', 'fev': '02',
    'mar': '03', 'march': '03', 'mär': '03', 'mars': '03', 'marz': '03',
    'apr': '04', 'april': '04', 'apri': '04',
    'may': '05', 'maj': '05', 'mai': '05',
    'jun': '06', 'june': '06', 'juni': '06',
    'jul': '07', 'july': '07', 'juli': '07',
    'aug': '08', 'august': '08',
    'sep': '09', 'sept': '09', 'september': '09',
    'oct': '10', 'october': '10', 'okt': '10',
    'nov': '11', 'november': '11',
    'dec': '12', 'december': '12',
}

STANDARD_RE = re.compile(r'^\d{2}-\d{2}-\d{4}$')

def month_lookup(s):
    """Look up month string, return MM or None."""
    return MONTHS.get(s.lower().rstrip('.'))

def parse_date(raw):
    """Parse non-standard date -> MM-DD-YYYY or None if already standard/unparseable."""
    if not raw or not raw.strip():
        return None
    s = raw.strip()

    # Already standard
    if STANDARD_RE.match(s):
        return None

    # Unparseable markers
    low = s.lower()
    if low in ('unknown', 'deceased', 'xx.xx.xxxx', ''):
        return None

    # --- Pattern matching, most specific first ---

    # "DD.MM.YYYY" European format
    m = re.match(r'^(\d{2})\.(\d{2})\.(\d{4})$', s)
    if m:
        dd, mm, yyyy = m.groups()
        return f"{mm}-{dd}-{yyyy}"

    # "DD/M YYYY" format like "27/5 1894"
    m = re.match(r'^(\d{1,2})/(\d{1,2})\s+(\d{4})$', s)
    if m:
        dd, mm, yyyy = m.groups()
        return f"{int(mm):02d}-{int(dd):02d}-{yyyy}"

    # "Month DD, YYYY" or "Month D, YYYY" (December 6, 1973)
    m = re.match(r'^(\w+)\.?\s+(\d{1,2}),?\s+(\d{4})$', s)
    if m:
        mon_s, day, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # "Mon DD YYYY" without comma (Aug. 18 1862)
    m = re.match(r'^(\w+)\.?\s+(\d{1,2})\s+(\d{4})$', s)
    if m:
        mon_s, day, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # "DD Mon YYYY" / "D Mon YYYY" - the big one
    m = re.match(r'^(\d{1,2})\s+(\w+)\s+(\d{4})$', s)
    if m:
        day, mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            d = int(day)
            return f"{mm}-{d:02d}-{year}" if d > 0 else f"{mm}-00-{year}"

    # "DD MON YYYY" uppercase (22 JAN 1903, 07 APR 2018)
    m = re.match(r'^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$', s)
    if m:
        day, mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            d = int(day)
            return f"{mm}-{d:02d}-{year}" if d > 0 else f"{mm}-00-{year}"

    # "Mon YYYY" / "Month YYYY" (Apr 1842, June, 1813)
    m = re.match(r'^(\w+),?\s+(\d{4})$', s)
    if m:
        mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-00-{year}"

    # "YYYYAD"
    m = re.match(r'^(\d{4})AD$', s, re.IGNORECASE)
    if m:
        return f"00-00-{m.group(1)}"

    # Pure year "YYYY"
    m = re.match(r'^(\d{4})$', s)
    if m:
        return f"00-00-{m.group(1)}"

    # "YYYY?" (1710?)
    m = re.match(r'^(\d{4})\?$', s)
    if m:
        return f"00-00-{m.group(1)}"

    # "YYYY/YY" or "YYYY/YYYY" (1655/58, 1724/1730)
    m = re.match(r'^(\d{4})/\d+$', s)
    if m:
        return f"00-00-{m.group(1)}"

    # Prefixed: Abt/About/Ca/Ca./c./est/um/Omkr/circa + YYYY
    m = re.match(r'^(?:Abt|About|Ca\.?|ca\.?|c\.?|est|um|Omkr|circa)\s+(\d{4})$', s, re.IGNORECASE)
    if m:
        return f"00-00-{m.group(1)}"

    # Prefixed: Bef/Aft/Before/After + YYYY
    m = re.match(r'^(?:Bef|Aft|Before|After|Etter|Efter|nach)\s+(\d{4})$', s, re.IGNORECASE)
    if m:
        return f"00-00-{m.group(1)}"

    # "Bet YYYY and YYYY"
    m = re.match(r'^Bet\.?\s+(\d{4})\s+and\s+(\d{4})$', s, re.IGNORECASE)
    if m:
        return f"00-00-{m.group(1)}"

    # "bet. YYYY-YYYY"
    m = re.match(r'^bet\.?\s+(\d{4})-(\d{4})$', s, re.IGNORECASE)
    if m:
        return f"00-00-{m.group(1)}"

    # Prefixed + "DD Mon YYYY" (Abt 25 May 1690, Bef 16 Jan 1725)
    m = re.match(r'^(?:Abt|About|Ca\.?|Bef|Aft|Before|After)\s+(\d{1,2})\s+(\w+)\s+(\d{4})$', s, re.IGNORECASE)
    if m:
        day, mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # Prefixed + "Mon YYYY" (Abt Aug 1645, Bef Aug 1610, Aft Mar 1722)
    m = re.match(r'^(?:Abt|About|Bef|Aft|Before|After|Christina)\s+(\w+)\s+(\d{4})$', s, re.IGNORECASE)
    if m:
        mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-00-{year}"

    # Prefixed + "Mon DD, YYYY" (Aft 8 Aug 1600 style already caught, but also "Aft 1 Sep 1606")
    m = re.match(r'^(?:Aft|Bef)\s+(\d{1,2})\s+(\w+)\s+(\d{4})$', s, re.IGNORECASE)
    if m:
        day, mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # "DD Month Abt YYYY" (12 September Abt 1808, 25 January Abt 1811, etc.)
    m = re.match(r'^(\d{1,2})\s+(\w+)\s+(?:Abt|About)\s+(\d{4})$', s, re.IGNORECASE)
    if m:
        day, mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # "D Month Abt YYYY" variant: "2 March Abt 1810"
    m = re.match(r'^(\d{1,2})\s+(\w+)\s+Abt\s+(\d{4})$', s, re.IGNORECASE)
    if m:
        day, mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # "12 February Abt 1733" -> already caught above

    # "(YYYYX)" like "(1654G)"
    m = re.match(r'^\((\d{4})\w*\)$', s)
    if m:
        return f"00-00-{m.group(1)}"

    # "DDMon YYYY" no space (24Jun 1848)
    m = re.match(r'^(\d{1,2})(\w{3,})\s+(\d{4})$', s)
    if m:
        day, mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # "DD Mon YYYY (extra)" - take first date (22 Apr 1577 (1581))
    m = re.match(r'^(\d{1,2})\s+(\w+)\s+(\d{4})\s*[\(/]', s)
    if m:
        day, mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # "DD Mon YYYY / extra" (24 Jun 1756 / 17 Jul 1756 bapt)
    m = re.match(r'^(\d{1,2})\s+(\w+)\s+(\d{4})\s*/\s', s)
    if m:
        day, mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # "DD Mon YYYY extra" (6 May 1711 bapt, 9 Oct 1665 (alt 1668))
    m = re.match(r'^(\d{1,2})\s+(\w+)\s+(\d{4})\s+', s)
    if m:
        day, mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # "11 Jan 1660/1" -> slash in year
    m = re.match(r'^(\d{1,2})\s+(\w+)\s+(\d{4})/\d+$', s)
    if m:
        day, mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # "Abt 1604 June 14" -> extract year
    m = re.match(r'^(?:Abt|About)\s+(\d{4})\s+(\w+)\s+(\d{1,2})$', s, re.IGNORECASE)
    if m:
        year, mon_s, day = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # "Bef 17 Jun 1673" -> already caught
    # "Bef 31 Oct 1683" -> already caught

    # "1880+" -> strip +
    m = re.match(r'^(\d{4})\+$', s)
    if m:
        return f"00-00-{m.group(1)}"

    # "YYYY extra text" - death dates with location (1615 Kallax 5, Luleå...)
    m = re.match(r'^(\d{4})\s+\w', s)
    if m:
        year = m.group(1)
        if 1000 <= int(year) <= 2030:
            return f"00-00-{year}"

    # "YYYY or YYYY" -> use first
    m = re.match(r'^(\d{4})\s+or\s+\d{4}$', s, re.IGNORECASE)
    if m:
        return f"00-00-{m.group(1)}"

    # "1650 or 1663" for death
    m = re.match(r'^(\d{4})\s+or\s+(\d{4})$', s, re.IGNORECASE)
    if m:
        return f"00-00-{m.group(1)}"

    # "1653/1663" -> first
    m = re.match(r'^(\d{4})/(\d{4})$', s)
    if m:
        return f"00-00-{m.group(1)}"

    # "April. 15, 1850" -> Month. DD, YYYY
    m = re.match(r'^(\w+)\.?\s+(\d{1,2}),?\s+(\d{4})$', s)
    if m:
        mon_s, day, year = m.groups()
        mm = month_lookup(mon_s.rstrip('.'))
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # "ca YYYY-MM" like "ca 1575-07"
    m = re.match(r'^ca\s+(\d{4})-(\d{2})$', s, re.IGNORECASE)
    if m:
        year, month = m.groups()
        return f"{month}-00-{year}"

    # "73 1568" -> bad day, use year only
    m = re.match(r'^\d+\s+(\d{4})$', s)
    if m:
        return f"00-00-{m.group(1)}"

    # "02 Nov 1587 OR 04 Sep 1603" -> use first date
    m = re.match(r'^(\d{1,2})\s+(\w+)\s+(\d{4})\s+OR\s', s, re.IGNORECASE)
    if m:
        day, mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # "04 Sep" (no year) -> skip
    m = re.match(r'^\d{2}\s+\w+$', s)
    if m:
        return None

    # "29 Oct 1490/91 or 1521" -> use 1521 as simpler
    m = re.match(r'.*(\d{4})$', s)
    if m:
        year = m.group(1)
        if 1000 <= int(year) <= 2030:
            # Try to get month/day from beginning
            m2 = re.match(r'^(\d{1,2})\s+(\w+)\s', s)
            if m2:
                day, mon_s = m2.groups()
                mm = month_lookup(mon_s)
                if mm:
                    return f"{mm}-{int(day):02d}-{year}"
            return f"00-00-{year}"

    # "10 June 1511/1576" -> take first
    m = re.match(r'^(\d{1,2})\s+(\w+)\s+(\d{4})', s)
    if m:
        day, mon_s, year = m.groups()
        mm = month_lookup(mon_s)
        if mm:
            return f"{mm}-{int(day):02d}-{year}"

    # Last resort: find any 4-digit year
    m = re.search(r'(\d{4})', s)
    if m:
        year = int(m.group(1))
        if 1000 <= year <= 2030:
            return f"00-00-{m.group(1)}"

    return None


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    birth_updates = []
    death_updates = []
    skipped_births = []
    skipped_deaths = []

    with driver.session() as session:
        # Fetch all non-standard birth dates
        result = session.run("""
            MATCH (p:GenPerson)
            WHERE p.birth_date IS NOT NULL AND p.birth_date <> ''
              AND NOT p.birth_date =~ '\\d{2}-\\d{2}-\\d{4}'
            RETURN elementId(p) AS eid, p.full_name AS name, p.birth_date AS date
        """)
        for record in result:
            new_date = parse_date(record["date"])
            if new_date:
                birth_updates.append((record["eid"], record["name"], record["date"], new_date))
            else:
                skipped_births.append((record["name"], record["date"]))

        # Fetch all non-standard death dates
        result = session.run("""
            MATCH (p:GenPerson)
            WHERE p.death_date IS NOT NULL AND p.death_date <> ''
              AND NOT p.death_date =~ '\\d{2}-\\d{2}-\\d{4}'
            RETURN elementId(p) AS eid, p.full_name AS name, p.death_date AS date
        """)
        for record in result:
            new_date = parse_date(record["date"])
            if new_date:
                death_updates.append((record["eid"], record["name"], record["date"], new_date))
            else:
                skipped_deaths.append((record["name"], record["date"]))

        # Apply birth date updates
        print(f"\n=== BIRTH DATE UPDATES: {len(birth_updates)} ===")
        for eid, name, old, new in birth_updates:
            session.run(
                "MATCH (p:GenPerson) WHERE elementId(p) = $eid SET p.birth_date = $new",
                eid=eid, new=new
            )
        print(f"✓ Applied {len(birth_updates)} birth date fixes")

        # Apply death date updates
        print(f"\n=== DEATH DATE UPDATES: {len(death_updates)} ===")
        for eid, name, old, new in death_updates:
            session.run(
                "MATCH (p:GenPerson) WHERE elementId(p) = $eid SET p.death_date = $new",
                eid=eid, new=new
            )
        print(f"✓ Applied {len(death_updates)} death date fixes")

    # Report skipped
    if skipped_births:
        print(f"\n=== SKIPPED BIRTHS ({len(skipped_births)}) ===")
        for name, date in skipped_births:
            print(f"  {name}: {date}")

    if skipped_deaths:
        print(f"\n=== SKIPPED DEATHS ({len(skipped_deaths)}) ===")
        for name, date in skipped_deaths:
            print(f"  {name}: {date}")

    # Verify
    with driver.session() as session:
        result = session.run("""
            MATCH (p:GenPerson)
            WHERE (p.birth_date IS NOT NULL AND p.birth_date <> ''
                   AND NOT p.birth_date =~ '\\d{2}-\\d{2}-\\d{4}')
               OR (p.death_date IS NOT NULL AND p.death_date <> ''
                   AND NOT p.death_date =~ '\\d{2}-\\d{2}-\\d{4}')
            RETURN count(p) AS remaining
        """)
        remaining = result.single()["remaining"]
        print(f"\n=== REMAINING NON-STANDARD: {remaining} ===")

    print(f"\n✓ TOTAL: {len(birth_updates)} births + {len(death_updates)} deaths = {len(birth_updates) + len(death_updates)} dates standardized")

    driver.close()

if __name__ == "__main__":
    main()

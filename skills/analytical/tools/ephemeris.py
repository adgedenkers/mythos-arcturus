#!/usr/bin/env python3
"""
Ephemeris Engine for Soul Stratigraphy
Swiss Ephemeris wrapper for natal, transit, and synastry calculations.

Supports three astrological frameworks:
  - Western Tropical (standard modern/psychological)
  - Hellenistic (Whole Sign houses, traditional dignities, sect)
  - Vedic/Jyotish (Lahiri ayanamsa, sidereal zodiac)

Usage:
    from ephemeris import calculate_natal, calculate_transits, calculate_synastry
"""

import swisseph as swe
import json
import sys
from datetime import datetime, timezone
from math import floor

# ─── Constants ───────────────────────────────────────────────────────────────

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
    'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN, 'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO, 'North Node': swe.MEAN_NODE
}

# Chiron requires Swiss Ephemeris data files; skip gracefully if unavailable
OPTIONAL_BODIES = {'Chiron': 15}

SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

ELEMENTS = {
    'Aries': 'Fire', 'Taurus': 'Earth', 'Gemini': 'Air', 'Cancer': 'Water',
    'Leo': 'Fire', 'Virgo': 'Earth', 'Libra': 'Air', 'Scorpio': 'Water',
    'Sagittarius': 'Fire', 'Capricorn': 'Earth', 'Aquarius': 'Air', 'Pisces': 'Water'
}

MODALITIES = {
    'Aries': 'Cardinal', 'Taurus': 'Fixed', 'Gemini': 'Mutable',
    'Cancer': 'Cardinal', 'Leo': 'Fixed', 'Virgo': 'Mutable',
    'Libra': 'Cardinal', 'Scorpio': 'Fixed', 'Sagittarius': 'Mutable',
    'Capricorn': 'Cardinal', 'Aquarius': 'Fixed', 'Pisces': 'Mutable'
}

# Traditional rulerships (Hellenistic)
TRADITIONAL_RULERS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
    'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
    'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}

# Modern rulerships
MODERN_RULERS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
    'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
    'Libra': 'Venus', 'Scorpio': 'Pluto', 'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn', 'Aquarius': 'Uranus', 'Pisces': 'Neptune'
}

# Essential dignities (traditional)
DIGNITIES = {
    'Sun': {'domicile': 'Leo', 'exaltation': 'Aries', 'detriment': 'Aquarius', 'fall': 'Libra'},
    'Moon': {'domicile': 'Cancer', 'exaltation': 'Taurus', 'detriment': 'Capricorn', 'fall': 'Scorpio'},
    'Mercury': {'domicile': ['Gemini', 'Virgo'], 'exaltation': 'Virgo', 'detriment': ['Sagittarius', 'Pisces'], 'fall': 'Pisces'},
    'Venus': {'domicile': ['Taurus', 'Libra'], 'exaltation': 'Pisces', 'detriment': ['Aries', 'Scorpio'], 'fall': 'Virgo'},
    'Mars': {'domicile': ['Aries', 'Scorpio'], 'exaltation': 'Capricorn', 'detriment': ['Taurus', 'Libra'], 'fall': 'Cancer'},
    'Jupiter': {'domicile': ['Sagittarius', 'Pisces'], 'exaltation': 'Cancer', 'detriment': ['Gemini', 'Virgo'], 'fall': 'Capricorn'},
    'Saturn': {'domicile': ['Capricorn', 'Aquarius'], 'exaltation': 'Libra', 'detriment': ['Cancer', 'Leo'], 'fall': 'Aries'},
}

# Vedic Nakshatras (27 lunar mansions)
NAKSHATRAS = [
    {'name': 'Ashwini', 'ruler': 'Ketu', 'start': 0.0},
    {'name': 'Bharani', 'ruler': 'Venus', 'start': 13.3333},
    {'name': 'Krittika', 'ruler': 'Sun', 'start': 26.6667},
    {'name': 'Rohini', 'ruler': 'Moon', 'start': 40.0},
    {'name': 'Mrigashira', 'ruler': 'Mars', 'start': 53.3333},
    {'name': 'Ardra', 'ruler': 'Rahu', 'start': 66.6667},
    {'name': 'Punarvasu', 'ruler': 'Jupiter', 'start': 80.0},
    {'name': 'Pushya', 'ruler': 'Saturn', 'start': 93.3333},
    {'name': 'Ashlesha', 'ruler': 'Mercury', 'start': 106.6667},
    {'name': 'Magha', 'ruler': 'Ketu', 'start': 120.0},
    {'name': 'Purva Phalguni', 'ruler': 'Venus', 'start': 133.3333},
    {'name': 'Uttara Phalguni', 'ruler': 'Sun', 'start': 146.6667},
    {'name': 'Hasta', 'ruler': 'Moon', 'start': 160.0},
    {'name': 'Chitra', 'ruler': 'Mars', 'start': 173.3333},
    {'name': 'Swati', 'ruler': 'Rahu', 'start': 186.6667},
    {'name': 'Vishakha', 'ruler': 'Jupiter', 'start': 200.0},
    {'name': 'Anuradha', 'ruler': 'Saturn', 'start': 213.3333},
    {'name': 'Jyeshtha', 'ruler': 'Mercury', 'start': 226.6667},
    {'name': 'Mula', 'ruler': 'Ketu', 'start': 240.0},
    {'name': 'Purva Ashadha', 'ruler': 'Venus', 'start': 253.3333},
    {'name': 'Uttara Ashadha', 'ruler': 'Sun', 'start': 266.6667},
    {'name': 'Shravana', 'ruler': 'Moon', 'start': 280.0},
    {'name': 'Dhanishtha', 'ruler': 'Mars', 'start': 293.3333},
    {'name': 'Shatabhisha', 'ruler': 'Rahu', 'start': 306.6667},
    {'name': 'Purva Bhadrapada', 'ruler': 'Jupiter', 'start': 320.0},
    {'name': 'Uttara Bhadrapada', 'ruler': 'Saturn', 'start': 333.3333},
    {'name': 'Revati', 'ruler': 'Mercury', 'start': 346.6667},
]

# Vimshottari Dasha periods (years)
DASHA_PERIODS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}
DASHA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
TOTAL_DASHA_YEARS = 120

ASPECT_DEFINITIONS = {
    'conjunction': {'angle': 0, 'orb': 8, 'symbol': '☌'},
    'opposition': {'angle': 180, 'orb': 8, 'symbol': '☍'},
    'trine': {'angle': 120, 'orb': 8, 'symbol': '△'},
    'square': {'angle': 90, 'orb': 7, 'symbol': '□'},
    'sextile': {'angle': 60, 'orb': 6, 'symbol': '⚹'},
    'quincunx': {'angle': 150, 'orb': 3, 'symbol': '⚻'},
    'semisquare': {'angle': 45, 'orb': 2, 'symbol': '∠'},
    'sesquiquadrate': {'angle': 135, 'orb': 2, 'symbol': '⚼'},
}


# ─── Helper Functions ────────────────────────────────────────────────────────

def lon_to_sign(longitude):
    """Convert ecliptic longitude to sign and degree."""
    sign_idx = int(longitude / 30) % 12
    degree = longitude % 30
    return SIGNS[sign_idx], degree

def format_position(longitude):
    """Format longitude as '15° 23' Aries'."""
    sign, deg = lon_to_sign(longitude)
    d = int(deg)
    m = int((deg - d) * 60)
    return f"{d}° {m:02d}' {sign}"

def get_nakshatra(sidereal_longitude):
    """Get Vedic nakshatra for a sidereal longitude."""
    nak_idx = int(sidereal_longitude / (360 / 27)) % 27
    nak = NAKSHATRAS[nak_idx]
    pada = int(((sidereal_longitude % (360/27)) / (360/27)) * 4) + 1
    return {'name': nak['name'], 'ruler': nak['ruler'], 'pada': min(pada, 4)}

def get_dignity(planet_name, sign):
    """Get essential dignity status for a planet in a sign."""
    if planet_name not in DIGNITIES:
        return None
    d = DIGNITIES[planet_name]
    for status in ['domicile', 'exaltation', 'detriment', 'fall']:
        val = d[status]
        if isinstance(val, list):
            if sign in val:
                return status
        elif sign == val:
            return status
    return 'peregrine'

def is_retrograde(speed):
    """Check if a body is retrograde (negative speed)."""
    return speed < 0

def calculate_aspect(lon1, lon2):
    """Calculate aspect between two longitudes."""
    diff = abs(lon1 - lon2) % 360
    if diff > 180:
        diff = 360 - diff
    for name, asp in ASPECT_DEFINITIONS.items():
        if abs(diff - asp['angle']) <= asp['orb']:
            orb = abs(diff - asp['angle'])
            applying = None  # Would need speeds to determine
            return {
                'aspect': name,
                'symbol': asp['symbol'],
                'angle': asp['angle'],
                'orb': round(orb, 2),
                'exact': orb < 1.0
            }
    return None

def determine_sect(sun_longitude, asc_longitude):
    """Determine if chart is diurnal or nocturnal (Hellenistic sect)."""
    # Sun above horizon = diurnal
    # Simplified: Sun in houses 7-12 (above horizon) = day chart
    # More accurate: check if Sun longitude is between DSC and ASC going through MC
    # For now, use the common approximation
    diff = (sun_longitude - asc_longitude) % 360
    return 'diurnal' if 180 < diff < 360 else 'nocturnal'

def get_sect_status(planet_name, sect):
    """Get sect membership for Hellenistic analysis."""
    diurnal_planets = ['Sun', 'Jupiter', 'Saturn']
    nocturnal_planets = ['Moon', 'Venus', 'Mars']
    if planet_name in diurnal_planets:
        return 'of sect' if sect == 'diurnal' else 'contrary to sect'
    elif planet_name in nocturnal_planets:
        return 'of sect' if sect == 'nocturnal' else 'contrary to sect'
    return 'neutral'  # Mercury

def compute_vimshottari_dasha(moon_sidereal_lon, birth_jd):
    """Compute Vimshottari Dasha periods from Moon's nakshatra position."""
    nak = get_nakshatra(moon_sidereal_lon)
    start_lord = nak['ruler']

    # How far through the nakshatra the Moon is
    nak_span = 360.0 / 27.0
    nak_start = ((moon_sidereal_lon // nak_span) * nak_span)
    progress = (moon_sidereal_lon - nak_start) / nak_span

    # Remaining portion of first dasha
    start_idx = DASHA_ORDER.index(start_lord)
    first_period_years = DASHA_PERIODS[start_lord]
    remaining_years = first_period_years * (1 - progress)

    dashas = []
    current_jd = birth_jd
    for i in range(18):  # ~2 full cycles, more than enough for a lifetime
        idx = (start_idx + i) % 9
        lord = DASHA_ORDER[idx]
        years = remaining_years if i == 0 else DASHA_PERIODS[lord]
        start_date = swe.revjul(current_jd)
        end_jd = current_jd + years * 365.25
        end_date = swe.revjul(end_jd)
        dashas.append({
            'lord': lord,
            'years': round(years, 2),
            'start': f"{int(start_date[0])}-{int(start_date[1]):02d}-{int(start_date[2]):02d}",
            'end': f"{int(end_date[0])}-{int(end_date[1]):02d}-{int(end_date[2]):02d}"
        })
        current_jd = end_jd
        if current_jd > birth_jd + 120 * 365.25:
            break

    return {'moon_nakshatra': nak, 'dashas': dashas}


# ─── Core Calculation Functions ──────────────────────────────────────────────

def calculate_planets(jd, flags=0):
    """Calculate positions for all planets at given Julian Day."""
    swe.set_ephe_path(None)  # Use built-in Moshier ephemeris
    results = {}
    for name, body_id in PLANETS.items():
        pos = swe.calc_ut(jd, body_id, flags)
        lon = pos[0][0]
        sign, deg = lon_to_sign(lon)
        results[name] = {
            'longitude': round(lon, 4),
            'latitude': round(pos[0][1], 4),
            'distance': round(pos[0][2], 6),
            'speed': round(pos[0][3], 4),
            'sign': sign,
            'degree_in_sign': round(deg, 4),
            'formatted': format_position(lon),
            'retrograde': is_retrograde(pos[0][3]),
            'element': ELEMENTS[sign],
            'modality': MODALITIES[sign],
        }
        # Add dignity for traditional planets
        dignity = get_dignity(name, sign)
        if dignity:
            results[name]['dignity'] = dignity
        results[name]['traditional_ruler'] = TRADITIONAL_RULERS[sign]
        results[name]['modern_ruler'] = MODERN_RULERS[sign]

    # Try optional bodies (Chiron)
    for name, body_id in OPTIONAL_BODIES.items():
        try:
            pos = swe.calc_ut(jd, body_id, flags)
            lon = pos[0][0]
            sign, deg = lon_to_sign(lon)
            results[name] = {
                'longitude': round(lon, 4),
                'sign': sign,
                'degree_in_sign': round(deg, 4),
                'formatted': format_position(lon),
                'retrograde': is_retrograde(pos[0][3]),
            }
        except:
            results[name] = {'note': 'Requires Swiss Ephemeris data files for calculation'}

    # South Node = opposite North Node
    if 'North Node' in results:
        nn_lon = results['North Node']['longitude']
        sn_lon = (nn_lon + 180) % 360
        sign, deg = lon_to_sign(sn_lon)
        results['South Node'] = {
            'longitude': round(sn_lon, 4),
            'sign': sign,
            'degree_in_sign': round(deg, 4),
            'formatted': format_position(sn_lon),
            'retrograde': True,  # Nodes always retrograde in mean calc
        }

    return results

def calculate_houses(jd, lat, lon, system='P'):
    """Calculate house cusps. Systems: P=Placidus, W=Whole Sign, B=Alcabitius, K=Koch."""
    swe.set_ephe_path(None)
    houses_data = swe.houses(jd, lat, lon, system.encode())
    cusps = houses_data[0]
    angles = houses_data[1]

    result = {
        'system': {'P': 'Placidus', 'W': 'Whole Sign', 'B': 'Alcabitius', 'K': 'Koch', 'E': 'Equal', 'R': 'Regiomontanus'}.get(system, system),
        'cusps': {},
        'angles': {
            'ASC': {'longitude': round(angles[0], 4), 'formatted': format_position(angles[0]), 'sign': lon_to_sign(angles[0])[0]},
            'MC': {'longitude': round(angles[1], 4), 'formatted': format_position(angles[1]), 'sign': lon_to_sign(angles[1])[0]},
            'DSC': {'longitude': round((angles[0] + 180) % 360, 4), 'formatted': format_position((angles[0] + 180) % 360)},
            'IC': {'longitude': round((angles[1] + 180) % 360, 4), 'formatted': format_position((angles[1] + 180) % 360)},
        }
    }
    for i, cusp in enumerate(cusps):
        result['cusps'][f'House {i+1}'] = {
            'longitude': round(cusp, 4),
            'formatted': format_position(cusp),
            'sign': lon_to_sign(cusp)[0]
        }
    return result

def assign_houses(planets, houses):
    """Assign planets to houses based on house cusps."""
    cusps = [houses['cusps'][f'House {i+1}']['longitude'] for i in range(12)]
    for name, data in planets.items():
        if 'longitude' not in data:
            continue
        lon = data['longitude']
        house = 12  # default
        for i in range(12):
            next_i = (i + 1) % 12
            start = cusps[i]
            end = cusps[next_i]
            if start < end:
                if start <= lon < end:
                    house = i + 1
                    break
            else:  # wraps around 0°
                if lon >= start or lon < end:
                    house = i + 1
                    break
        data['house'] = house
    return planets

def calculate_aspects(planets):
    """Calculate all aspects between planets."""
    aspects = []
    planet_names = [n for n in planets if 'longitude' in planets[n]]
    for i, name1 in enumerate(planet_names):
        for name2 in planet_names[i+1:]:
            asp = calculate_aspect(planets[name1]['longitude'], planets[name2]['longitude'])
            if asp:
                asp['planet1'] = name1
                asp['planet2'] = name2
                aspects.append(asp)
    return aspects

def calculate_vedic_layer(jd, planets):
    """Calculate Vedic/sidereal positions and dashas."""
    swe.set_ephe_path(None)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    vedic = {
        'ayanamsa': round(ayanamsa, 4),
        'ayanamsa_type': 'Lahiri',
        'planets': {}
    }

    for name, data in planets.items():
        if 'longitude' not in data:
            continue
        sid_lon = (data['longitude'] - ayanamsa) % 360
        sign, deg = lon_to_sign(sid_lon)
        vedic['planets'][name] = {
            'sidereal_longitude': round(sid_lon, 4),
            'sign': sign,
            'degree_in_sign': round(deg, 4),
            'formatted': format_position(sid_lon),
            'nakshatra': get_nakshatra(sid_lon),
        }

    # Vimshottari Dasha from Moon's sidereal position
    if 'Moon' in vedic['planets']:
        moon_sid = vedic['planets']['Moon']['sidereal_longitude']
        vedic['dasha'] = compute_vimshottari_dasha(moon_sid, jd)

    return vedic


# ─── Main Calculation Endpoints ──────────────────────────────────────────────

def calculate_natal(year, month, day, hour, minute, lat, lon, tz_offset=0, name=None):
    """
    Full natal chart calculation across all three frameworks.

    Args:
        year, month, day: Birth date
        hour, minute: Birth time (local)
        lat, lon: Birth location coordinates
        tz_offset: Hours from UTC (e.g., -5 for EST)
        name: Optional name label
    """
    # Convert local time to UT
    ut_hour = hour + minute/60.0 - tz_offset
    jd = swe.julday(year, month, day, ut_hour)

    # Core tropical positions
    planets = calculate_planets(jd)

    # ── Western Tropical Layer ──
    western_houses = calculate_houses(jd, lat, lon, 'P')  # Placidus
    western_planets = assign_houses(dict(planets), western_houses)  # copy
    western_aspects = calculate_aspects(planets)

    # Sect determination
    sect = determine_sect(planets['Sun']['longitude'], western_houses['angles']['ASC']['longitude'])
    for name_p, data in western_planets.items():
        if 'longitude' in data:
            data['sect'] = get_sect_status(name_p, sect)

    # ── Hellenistic Layer ──
    hellenistic_houses = calculate_houses(jd, lat, lon, 'W')  # Whole Sign
    hellenistic_planets = assign_houses(dict(planets), hellenistic_houses)

    # ── Vedic Layer ──
    vedic = calculate_vedic_layer(jd, planets)
    vedic_houses = calculate_houses(jd, lat, lon, 'W')  # Whole Sign for Vedic too

    # Element/modality distribution
    element_count = {'Fire': 0, 'Earth': 0, 'Air': 0, 'Water': 0}
    modality_count = {'Cardinal': 0, 'Fixed': 0, 'Mutable': 0}
    for p_name in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
        if p_name in planets and 'element' in planets[p_name]:
            element_count[planets[p_name]['element']] += 1
            modality_count[planets[p_name]['modality']] += 1

    result = {
        'meta': {
            'name': name,
            'birth_date': f"{year}-{month:02d}-{day:02d}",
            'birth_time': f"{hour:02d}:{minute:02d}",
            'timezone_offset': tz_offset,
            'latitude': lat,
            'longitude': lon,
            'julian_day': jd,
            'calculation_type': 'natal',
            'framework': 'soul_stratigraphy'
        },
        'western_tropical': {
            'planets': western_planets,
            'houses': western_houses,
            'aspects': western_aspects,
            'sect': sect,
        },
        'hellenistic': {
            'planets': hellenistic_planets,
            'houses': hellenistic_houses,
            'aspects': western_aspects,  # Same aspects, different house placement
            'sect': sect,
        },
        'vedic': vedic,
        'synthesis': {
            'element_balance': element_count,
            'modality_balance': modality_count,
            'dominant_element': max(element_count, key=element_count.get),
            'dominant_modality': max(modality_count, key=modality_count.get),
            'asc_sign_tropical': western_houses['angles']['ASC']['sign'],
            'asc_sign_sidereal': lon_to_sign((western_houses['angles']['ASC']['longitude'] - vedic['ayanamsa']) % 360)[0],
            'sun_sign_tropical': planets['Sun']['sign'],
            'moon_sign_tropical': planets['Moon']['sign'],
            'sun_sign_sidereal': vedic['planets']['Sun']['sign'] if 'Sun' in vedic['planets'] else None,
            'moon_sign_sidereal': vedic['planets']['Moon']['sign'] if 'Moon' in vedic['planets'] else None,
            'moon_nakshatra': vedic['planets']['Moon']['nakshatra']['name'] if 'Moon' in vedic['planets'] else None,
        }
    }

    return result


def calculate_transits(natal_data, transit_year, transit_month, transit_day,
                       transit_hour=12, transit_minute=0, tz_offset=0):
    """
    Calculate current transits against a natal chart.

    Args:
        natal_data: Output from calculate_natal()
        transit_year..transit_minute: Transit date/time
        tz_offset: Hours from UTC
    """
    ut_hour = transit_hour + transit_minute/60.0 - tz_offset
    jd = swe.julday(transit_year, transit_month, transit_day, ut_hour)

    transit_planets = calculate_planets(jd)

    # Aspects from transiting planets to natal planets
    natal_planets = natal_data['western_tropical']['planets']
    transit_aspects = []
    for t_name, t_data in transit_planets.items():
        if 'longitude' not in t_data:
            continue
        for n_name, n_data in natal_planets.items():
            if 'longitude' not in n_data:
                continue
            asp = calculate_aspect(t_data['longitude'], n_data['longitude'])
            if asp:
                asp['transit_planet'] = t_name
                asp['natal_planet'] = n_name
                transit_aspects.append(asp)

    # Vedic transit layer
    vedic_transit = calculate_vedic_layer(jd, transit_planets)

    # Current dasha period (from natal)
    current_dasha = None
    if 'dasha' in natal_data['vedic']:
        # Find which dasha period the transit date falls in
        # (simplified - uses the natal dasha timeline)
        transit_date_str = f"{transit_year}-{transit_month:02d}-{transit_day:02d}"
        for d in natal_data['vedic']['dasha']['dashas']:
            if d['start'] <= transit_date_str <= d['end']:
                current_dasha = d
                break

    return {
        'meta': {
            'transit_date': f"{transit_year}-{transit_month:02d}-{transit_day:02d}",
            'transit_time': f"{transit_hour:02d}:{transit_minute:02d}",
            'julian_day': jd,
            'calculation_type': 'transit'
        },
        'transit_planets': transit_planets,
        'transit_to_natal_aspects': transit_aspects,
        'vedic_transits': vedic_transit,
        'current_dasha': current_dasha,
    }


def calculate_synastry(chart_a, chart_b):
    """
    Calculate synastry between two natal charts.

    Args:
        chart_a, chart_b: Outputs from calculate_natal()
    """
    planets_a = chart_a['western_tropical']['planets']
    planets_b = chart_b['western_tropical']['planets']

    # Cross-aspects
    cross_aspects = []
    for a_name, a_data in planets_a.items():
        if 'longitude' not in a_data:
            continue
        for b_name, b_data in planets_b.items():
            if 'longitude' not in b_data:
                continue
            asp = calculate_aspect(a_data['longitude'], b_data['longitude'])
            if asp:
                asp['person_a_planet'] = a_name
                asp['person_b_planet'] = b_name
                cross_aspects.append(asp)

    # House overlays (A's planets in B's houses and vice versa)
    overlay_a_in_b = {}
    for a_name, a_data in planets_a.items():
        if 'longitude' not in a_data:
            continue
        # Which house of B does A's planet fall in?
        temp = {a_name: dict(a_data)}
        assigned = assign_houses(temp, chart_b['western_tropical']['houses'])
        overlay_a_in_b[a_name] = assigned[a_name].get('house')

    overlay_b_in_a = {}
    for b_name, b_data in planets_b.items():
        if 'longitude' not in b_data:
            continue
        temp = {b_name: dict(b_data)}
        assigned = assign_houses(temp, chart_a['western_tropical']['houses'])
        overlay_b_in_a[b_name] = assigned[b_name].get('house')

    # Vedic compatibility (basic Kuta/Nakshatra comparison)
    vedic_compat = {}
    if 'vedic' in chart_a and 'vedic' in chart_b:
        moon_a = chart_a['vedic'].get('planets', {}).get('Moon', {})
        moon_b = chart_b['vedic'].get('planets', {}).get('Moon', {})
        if moon_a and moon_b:
            vedic_compat = {
                'moon_a_nakshatra': moon_a.get('nakshatra', {}).get('name'),
                'moon_b_nakshatra': moon_b.get('nakshatra', {}).get('name'),
                'moon_a_sign': moon_a.get('sign'),
                'moon_b_sign': moon_b.get('sign'),
            }

    return {
        'meta': {
            'person_a': chart_a['meta'].get('name', 'Person A'),
            'person_b': chart_b['meta'].get('name', 'Person B'),
            'calculation_type': 'synastry'
        },
        'cross_aspects': cross_aspects,
        'overlay_a_in_b_houses': overlay_a_in_b,
        'overlay_b_in_a_houses': overlay_b_in_a,
        'vedic_compatibility': vedic_compat,
    }


# ─── CLI Interface ───────────────────────────────────────────────────────────

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Soul Stratigraphy Ephemeris Engine')
    parser.add_argument('mode', choices=['natal', 'transit', 'synastry'], help='Calculation mode')
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--month', type=int, required=True)
    parser.add_argument('--day', type=int, required=True)
    parser.add_argument('--hour', type=int, default=12)
    parser.add_argument('--minute', type=int, default=0)
    parser.add_argument('--lat', type=float, required=True)
    parser.add_argument('--lon', type=float, required=True)
    parser.add_argument('--tz', type=float, default=0, help='Timezone offset from UTC')
    parser.add_argument('--name', type=str, default=None)
    parser.add_argument('--output', type=str, default=None, help='Output JSON file')

    args = parser.parse_args()

    if args.mode == 'natal':
        result = calculate_natal(
            args.year, args.month, args.day, args.hour, args.minute,
            args.lat, args.lon, args.tz, args.name
        )
    else:
        print(f"Mode '{args.mode}' requires additional inputs. Use as a library.", file=sys.stderr)
        sys.exit(1)

    output = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)

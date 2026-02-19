"""
Weather service for Mythos.
Fetches weather from Open-Meteo (no API key needed).
Used by:
  - /weather command in Telegram
  - Morning briefing analyst
  - Iris conversational queries
"""

import json
import logging
import urllib.request
import urllib.parse
from datetime import date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# Weather code descriptions (WMO codes)
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}

# Default location
DEFAULT_LAT = 42.44
DEFAULT_LON = -75.60
DEFAULT_NAME = "Oxford, NY"


def _geocode(query: str) -> Optional[dict]:
    """Geocode a location string (city/state or zip code) using Open-Meteo geocoding API."""
    try:
        # Check if it's a US zip code
        clean = query.strip()
        if clean.isdigit() and len(clean) == 5:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={clean}&count=1&language=en&format=json&country_code=US"
        else:
            encoded = urllib.parse.quote(clean)
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded}&count=1&language=en&format=json"

        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())

        results = data.get('results', [])
        if results:
            r = results[0]
            name = r.get('name', clean)
            admin1 = r.get('admin1', '')
            country = r.get('country_code', '')
            if admin1:
                display = f"{name}, {admin1}"
            else:
                display = f"{name}, {country}"
            return {
                'lat': r['latitude'],
                'lon': r['longitude'],
                'name': display,
            }
    except Exception as e:
        logger.warning(f"Geocode failed for '{query}': {e}")
    return None


def fetch_weather(lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON) -> Optional[dict]:
    """Fetch weather data from Open-Meteo."""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,apparent_temperature,wind_speed_10m,wind_gusts_10m,"
            f"relative_humidity_2m,precipitation,snowfall,weather_code"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,snowfall_sum,"
            f"precipitation_probability_max,weather_code,sunrise,sunset"
            f"&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch"
            f"&timezone=America/New_York&forecast_days=5"
        )
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")
        return None


def format_weather_telegram(data: dict, location_name: str = DEFAULT_NAME) -> str:
    """Format weather data as a Telegram message."""
    if not data:
        return "Weather data unavailable."

    current = data.get('current', {})
    daily = data.get('daily', {})

    temp = current.get('temperature_2m', '?')
    feels_like = current.get('apparent_temperature', '?')
    wind = current.get('wind_speed_10m', '?')
    gusts = current.get('wind_gusts_10m', '?')
    humidity = current.get('relative_humidity_2m', '?')
    precip = current.get('precipitation', 0)
    snow = current.get('snowfall', 0)
    code = current.get('weather_code', 0)
    condition = WEATHER_CODES.get(code, "Unknown")

    lines = [
        f"🌤 *Weather: {location_name}*",
        f"",
        f"*Now:* {condition}",
        f"🌡 {temp}°F (feels like {feels_like}°F)",
        f"💨 Wind {wind} mph, gusts {gusts} mph",
        f"💧 Humidity {humidity}%",
    ]

    if precip > 0:
        lines.append(f"🌧 Precipitation: {precip} in")
    if snow > 0:
        lines.append(f"❄️ Snowfall: {snow} in")

    # Daily forecast
    dates = daily.get('time', [])
    highs = daily.get('temperature_2m_max', [])
    lows = daily.get('temperature_2m_min', [])
    snow_sums = daily.get('snowfall_sum', [])
    precip_sums = daily.get('precipitation_sum', [])
    precip_probs = daily.get('precipitation_probability_max', [])
    codes = daily.get('weather_code', [])
    sunrises = daily.get('sunrise', [])
    sunsets = daily.get('sunset', [])

    lines.append("")
    lines.append("*Forecast:*")

    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    today = date.today()

    for i in range(min(5, len(dates))):
        d = today + timedelta(days=i)
        day_label = "Today" if i == 0 else ("Tomorrow" if i == 1 else day_names[d.weekday()])
        cond = WEATHER_CODES.get(codes[i] if i < len(codes) else 0, "")
        hi = highs[i] if i < len(highs) else '?'
        lo = lows[i] if i < len(lows) else '?'
        snow_i = snow_sums[i] if i < len(snow_sums) else 0
        precip_prob = precip_probs[i] if i < len(precip_probs) else 0

        line = f"  {day_label}: {hi}°/{lo}° {cond}"
        if snow_i > 0:
            line += f" ❄️{snow_i}in"
        if precip_prob > 30:
            line += f" ({precip_prob}% precip)"
        lines.append(line)

    # Snow day prediction (if tomorrow is a weekday)
    tomorrow = today + timedelta(days=1)
    if tomorrow.weekday() < 5 and len(snow_sums) > 1:
        tonight_snow = (snow_sums[0] if snow_sums[0] else 0) + (snow_sums[1] if snow_sums[1] else 0)
        if tonight_snow >= 12:
            lines.append(f"\n🏠 *Snow Day Likelihood: HIGH* ({tonight_snow} in forecast)")
        elif tonight_snow >= 8:
            lines.append(f"\n🏠 *Snow Day Likelihood: MODERATE* ({tonight_snow} in forecast)")
        elif tonight_snow >= 5:
            lines.append(f"\n🏠 *Snow Day Likelihood: LOW* ({tonight_snow} in forecast)")

    # Sunrise/sunset for today
    if sunrises and sunsets:
        sunrise_time = sunrises[0].split('T')[1] if 'T' in sunrises[0] else sunrises[0]
        sunset_time = sunsets[0].split('T')[1] if 'T' in sunsets[0] else sunsets[0]
        lines.append(f"\n🌅 Sunrise {sunrise_time} | 🌇 Sunset {sunset_time}")

    return "\n".join(lines)


def format_weather_for_analyst(data: dict) -> str:
    """Format weather data as plain text for the backlog analyst prompt."""
    if not data:
        return "  Weather data unavailable"

    current = data.get('current', {})
    daily = data.get('daily', {})

    lines = []

    temp = current.get('temperature_2m', '?')
    wind = current.get('wind_speed_10m', '?')
    precip = current.get('precipitation', 0)
    snow = current.get('snowfall', 0)
    code = current.get('weather_code', 0)
    condition = WEATHER_CODES.get(code, "Unknown")

    lines.append(f"  Current: {temp}F, {condition}, wind {wind} mph, precip {precip} in, snow {snow} in")

    dates = daily.get('time', [])
    highs = daily.get('temperature_2m_max', [])
    lows = daily.get('temperature_2m_min', [])
    snow_sums = daily.get('snowfall_sum', [])
    precip_sums = daily.get('precipitation_sum', [])

    for i in range(min(3, len(dates))):
        lines.append(
            f"  {dates[i]}: High {highs[i]}F / Low {lows[i]}F, "
            f"precip {precip_sums[i]} in, snow {snow_sums[i]} in"
        )

    # Snow day indicator
    from datetime import date as _date, timedelta as _td
    tomorrow = _date.today() + _td(days=1)
    if tomorrow.weekday() < 5 and len(snow_sums) > 1:
        tonight_snow = (snow_sums[0] or 0) + (snow_sums[1] or 0)
        if tonight_snow >= 12:
            lines.append(f"  SNOW DAY LIKELIHOOD: HIGH (forecast {tonight_snow} in snow)")
        elif tonight_snow >= 8:
            lines.append(f"  SNOW DAY LIKELIHOOD: MODERATE (forecast {tonight_snow} in snow)")
        elif tonight_snow >= 5:
            lines.append(f"  SNOW DAY LIKELIHOOD: LOW (forecast {tonight_snow} in snow)")
        else:
            lines.append(f"  Snow day unlikely ({tonight_snow} in forecast)")

    return "\n".join(lines)

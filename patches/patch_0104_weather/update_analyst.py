"""
Update backlog_analyst.py to use the shared weather_service module
instead of inline weather fetching code.
"""

path = '/opt/mythos/core/backlog_analyst.py'
with open(path) as f:
    content = f.read()

# Replace inline weather gathering with weather_service call
old_weather_gather = """        # Weather for Oxford, NY (lat 42.44, lon -75.60)
        try:
            import urllib.request, json as _json
            weather_url = (
                "https://api.open-meteo.com/v1/forecast?"
                "latitude=42.44&longitude=-75.60"
                "&current=temperature_2m,wind_speed_10m,precipitation,snowfall,weather_code"
                "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,snowfall_sum,weather_code"
                "&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch"
                "&timezone=America/New_York&forecast_days=3"
            )
            with urllib.request.urlopen(weather_url, timeout=10) as resp:
                state['weather'] = _json.loads(resp.read())
        except Exception as e:
            logger.warning(f"Weather fetch failed: {e}")
            state['weather'] = None"""

new_weather_gather = """        # Weather
        try:
            from core.weather_service import fetch_weather
            state['weather'] = fetch_weather()
        except Exception as e:
            logger.warning(f"Weather fetch failed: {e}")
            state['weather'] = None"""

if old_weather_gather in content:
    content = content.replace(old_weather_gather, new_weather_gather)
    print("Replaced inline weather fetch with weather_service call")
else:
    print("WARNING: Could not find inline weather code to replace")

# Replace inline weather prompt building with weather_service formatter
# Find the weather section in _build_prompt
old_weather_prompt_start = '        # Weather\n        prompt_parts.append("\\n=== WEATHER (Oxford, NY) ===")'
new_weather_prompt = '''        # Weather
        prompt_parts.append("\\n=== WEATHER (Oxford, NY) ===")
        try:
            from core.weather_service import format_weather_for_analyst
            wx_text = format_weather_for_analyst(state.get('weather'))
            prompt_parts.append(wx_text)
        except Exception:
            prompt_parts.append("  Weather data unavailable")'''

# Find and replace the entire weather prompt section
# It starts with "# Weather" and ends before "prompt_parts.append("\\n=== TODAY'S ROUTINES ===")"
import re
weather_section_pattern = r'        # Weather\n        prompt_parts\.append\("\\n=== WEATHER \(Oxford, NY\) ==="\)\n.*?(?=        prompt_parts\.append\("\\n=== TODAY\'S ROUTINES ===")'
match = re.search(weather_section_pattern, content, re.DOTALL)
if match:
    content = content[:match.start()] + new_weather_prompt + "\n\n" + content[match.end():]
    print("Replaced inline weather prompt with weather_service formatter")
else:
    print("WARNING: Could not find weather prompt section to replace")

with open(path, 'w') as f:
    f.write(content)

print("Done - analyst now uses weather_service module")

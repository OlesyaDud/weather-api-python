import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# ── Load environment variables ───────────────────────────────────────────────
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
HTTP_PROXY = os.getenv("HTTP_PROXY")
HTTPS_PROXY = os.getenv("HTTPS_PROXY")

if not API_KEY:
    raise RuntimeError("OPENWEATHER_API_KEY not found in .env")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

PROXIES = {}
if HTTP_PROXY:
    PROXIES["http"] = HTTP_PROXY
if HTTPS_PROXY:
    PROXIES["https"] = HTTPS_PROXY


# ── Helpers ──────────────────────────────────────────────────────────────────
def format_time(unix_time: int) -> str:
    return datetime.fromtimestamp(unix_time).strftime("%H:%M")


def get_location():
    """
    Returns a query string suitable for OpenWeatherMap.
    Examples:
      Paris,FR
      Berlin,DE
      Greenville,NC,US
    """
    while True:
        raw = input(
            "\n🌍 Enter city and country (US cities need state, e.g. Greenville,SC,US): "
        ).strip()

        if not raw:
            print("⚠️  Input cannot be empty.")
            continue

        parts = [p.strip() for p in raw.split(",")]

        # US requires city,state,US
        if len(parts) == 3 and parts[2].upper() == "US":
            city, state, country = parts
            if len(state) != 2 or not state.isalpha():
                print("⚠️  US state code must be 2 letters (CA, NY, TX...).")
                continue
            return f"{city},{state.upper()},{country.upper()}"

        # Other countries: city,country
        if len(parts) == 2:
            city, country = parts
            if len(country) != 2 or not country.isalpha():
                print("⚠️  Country code must be 2 letters (FR, DE, JP...).")
                continue
            return f"{city},{country.upper()}"

        print("⚠️  Invalid format.")
        print("   Examples:")
        print("   • Paris,FR")
        print("   • Tokyo,JP")
        print("   • Greenville,NC,US")


def fetch_weather(query: str):
    params = {
        "q": query,
        "appid": API_KEY,
        "units": "metric",
        "lang": "en",
    }

    try:
        r = requests.get(
            BASE_URL,
            params=params,
            proxies=PROXIES if PROXIES else None,
            timeout=10,
        )
        return r.status_code, r.json()

    except requests.exceptions.RequestException as e:
        return None, {"message": str(e)}


def display_weather(data: dict):
    city = data["name"]
    country = data["sys"]["country"]

    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]

    wind = data["wind"]["speed"]
    desc = data["weather"][0]["description"].capitalize()

    sunrise = format_time(data["sys"]["sunrise"])
    sunset = format_time(data["sys"]["sunset"])

    if temp <= 0:
        mood = "🧊 Freezing"
    elif temp < 10:
        mood = "🧥 Cold"
    elif temp < 25:
        mood = "🙂 Comfortable"
    else:
        mood = "🥵 Hot"

    print("\n" + "═" * 46)
    print(f"📍 {city}, {country}")
    print(f"📝 {desc}")
    print(f"🌡️  {temp}°C (feels like {feels}°C) — {mood}")
    print(f"💧 Humidity: {humidity}%")
    print(f"🌬️  Wind speed: {wind} m/s")
    print(f"🧭 Pressure: {pressure} hPa")
    print(f"🌅 Sunrise: {sunrise}   🌇 Sunset: {sunset}")
    print("═" * 46)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("🌦️  Weather Buddy")
    print("US cities require state code (e.g. Greenville,NC,US)")

    if PROXIES:
        print("🔌 Proxy enabled")

    while True:
        query = get_location()
        status, data = fetch_weather(query)

        if status == 200:
            display_weather(data)
        else:
            print("\n❌ Error:", data.get("message", "Unknown error"))

        again = input("\n🔁 Check another city? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()

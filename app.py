from pathlib import Path

from flask import Flask, render_template, request
import requests
import os
import datetime

_ROOT = Path(__file__).resolve().parent
try:
    from dotenv import load_dotenv

    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

app = Flask(__name__)

BASE = "https://api.openweathermap.org/data/2.5"
IMG = "https://openweathermap.org/img/wn"

# Render / local: set exactly OPENWEATHER_API_KEY (also accepts common typos).
_ENV_KEY_NAMES = (
    "OPENWEATHER_API_KEY",
    "OPEN_WEATHER_API_KEY",
    "OWM_API_KEY",
)


def openweather_api_key():
    for name in _ENV_KEY_NAMES:
        v = os.environ.get(name, "").strip()
        if v:
            return v
    return ""

# OpenWeather "main" -> UI theme (CSS class suffix)
THEME_HEX = {
    "default": "#0f172a",
    "clear": "#c2410c",
    "clouds": "#475569",
    "rain": "#1d4ed8",
    "drizzle": "#155e75",
    "storm": "#3730a3",
    "snow": "#334155",
    "fog": "#57534e",
}

THEME_BY_MAIN = {
    "clear": "clear",
    "clouds": "clouds",
    "rain": "rain",
    "drizzle": "drizzle",
    "thunderstorm": "storm",
    "snow": "snow",
    "mist": "fog",
    "smoke": "fog",
    "haze": "fog",
    "fog": "fog",
    "dust": "fog",
    "sand": "fog",
    "ash": "fog",
    "squall": "storm",
    "tornado": "storm",
}


def theme_from_weather(data):
    if not data or "weather" not in data or not data["weather"]:
        return "default"
    main = data["weather"][0].get("main", "").lower()
    return THEME_BY_MAIN.get(main, "default")


@app.route("/", methods=["GET", "POST"])
def home():
    weather = None
    forecast = []
    error = None
    theme = "default"
    api_key = openweather_api_key()

    if not api_key:
        error = (
            "API key Render-il set aakkiyitilla. Steps: render.com → Web Service (weather_app) → "
            "Environment → Add Environment Variable → Key must be exactly OPENWEATHER_API_KEY "
            "→ Value = OpenWeather key → Save → Manual Deploy (Clear build cache optional). "
            "Local: .env file same folder as app.py."
        )
        return render_template(
            "index.html",
            weather=weather,
            forecast=forecast,
            error=error,
            theme=theme,
            theme_color=THEME_HEX["default"],
            img_base=IMG,
        )

    if request.method == "POST":
        city = (request.form.get("city") or "").strip()
        if not city:
            error = "City enter cheyyu."
        else:
            params = {"q": city, "appid": api_key, "units": "metric"}
            res = requests.get(f"{BASE}/weather", params=params, timeout=10)

            if res.status_code == 200:
                data = res.json()
                theme = theme_from_weather(data)

                weather = {
                    "city": data["name"],
                    "country": data.get("sys", {}).get("country", ""),
                    "temperature": round(data["main"]["temp"]),
                    "feels_like": round(data["main"]["feels_like"]),
                    "description": data["weather"][0]["description"].title(),
                    "humidity": data["main"]["humidity"],
                    "wind": round(data.get("wind", {}).get("speed", 0) * 3.6),
                    "icon": data["weather"][0]["icon"],
                }

                f_res = requests.get(f"{BASE}/forecast", params=params, timeout=10)
                if f_res.status_code == 200:
                    f_data = f_res.json()
                    lst = f_data.get("list") or []
                    for i in range(0, min(len(lst), 40), 8):
                        day = lst[i]
                        forecast.append({
                            "temp": round(day["main"]["temp"]),
                            "icon": day["weather"][0]["icon"],
                            "day": datetime.datetime.fromtimestamp(day["dt"]).strftime("%a"),
                        })
            elif res.status_code == 404:
                error = "City kittiyilla — spelling check cheyyu."
            else:
                error = "Weather load cheyyan pattilla. Oru nimisham wait cheythu try cheyyu."

    return render_template(
        "index.html",
        weather=weather,
        forecast=forecast,
        error=error,
        theme=theme,
        theme_color=THEME_HEX.get(theme, THEME_HEX["default"]),
        img_base=IMG,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

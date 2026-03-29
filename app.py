from flask import Flask, render_template, request
import requests
import os
import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

API_KEY = os.environ.get("fa476182e7c6a7459a3e4a3f4057b19d", "").strip()
BASE = "https://api.openweathermap.org/data/2.5"
IMG = "https://openweathermap.org/img/wn"

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

    if not API_KEY:
        error = "Server missing OPENWEATHER_API_KEY. Add it in .env (local) or host env (Render)."
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
            params = {"q": city, "appid": API_KEY, "units": "metric"}
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

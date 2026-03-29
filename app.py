from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.environ.get("fa476182e7c6a7459a3e4a3f4057b19d")

@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    forecast = []

    if request.method == "POST":
        city = request.form.get("city")

        # 🔥 Current weather
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url).json()

        if res.get("cod") == 200:
            weather = {
                "city": res["name"],
                "temp": res["main"]["temp"],
                "desc": res["weather"][0]["description"],
                "icon": res["weather"][0]["icon"]
            }

            # 🔥 5-day forecast
            f_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
            f_res = requests.get(f_url).json()

            for i in range(0, 40, 8):  # daily data
                day = f_res["list"][i]
                forecast.append({
                    "temp": day["main"]["temp"],
                    "icon": day["weather"][0]["icon"],
                    "time": day["dt_txt"].split(" ")[0]
                })

    return render_template("index.html", weather=weather, forecast=forecast)


# 📍 LOCATION API
@app.route("/location", methods=["POST"])
def location():
    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    res = requests.get(url).json()

    return jsonify(res)


# ✅ Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
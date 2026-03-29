from flask import Flask, render_template, request
import requests
import os
import datetime

app = Flask(__name__)

# 🔑 PUT YOUR API KEY HERE
API_KEY = "fa476182e7c6a7459a3e4a3f4057b19d"

@app.route("/", methods=["GET", "POST"])
def home():
    weather = None
    forecast = []
    error = None

    if request.method == "POST":
        city = request.form.get("city")

        if city:
            # 🔹 Current Weather
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            res = requests.get(url)

            if res.status_code == 200:
                data = res.json()

                weather = {
                    "city": data["name"],
                    "temperature": data["main"]["temp"],
                    "description": data["weather"][0]["description"],
                    "humidity": data["main"]["humidity"],
                    "icon": data["weather"][0]["icon"]
                }

                # 🔹 5 Day Forecast
                f_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
                f_res = requests.get(f_url)
                f_data = f_res.json()

                for i in range(0, 40, 8):  # 5 days
                    day = f_data["list"][i]

                    forecast.append({
                        "temp": day["main"]["temp"],
                        "icon": day["weather"][0]["icon"],
                        "day": datetime.datetime.fromtimestamp(day["dt"]).strftime('%a')
                    })

            else:
                error = "City not found!"

    return render_template("index.html", weather=weather, forecast=forecast, error=error)


# 🔥 RENDER DEPLOY FIX
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
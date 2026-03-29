from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

# 🔑 Replace with your OpenWeather API key
API_KEY = "fa476182e7c6a7459a3e4a3f4057b19d"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/location', methods=['POST'])
def location():
    city = request.form.get('city')

    if not city:
        return render_template("index.html", error="Please enter a city name")

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)

    if response.status_code != 200:
        return render_template("index.html", error="City not found!")

    data = response.json()

    weather_data = {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"]
    }

    return render_template("index.html", weather=weather_data)


# 🔥 IMPORTANT FOR RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
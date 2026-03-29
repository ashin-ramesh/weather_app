from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "fa476182e7c6a7459a3e4a3f4057b19d"

# 🔥 Try Firebase (optional)
try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    firebase_enabled = True
    print("✅ Firebase Connected")

except Exception as e:
    firebase_enabled = False
    print("❌ Firebase Disabled:", e)


@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    history = []

    # 🔥 Get history (only if Firebase works)
    if firebase_enabled:
        try:
            docs = db.collection("history").stream()
            for doc in docs:
                history.append(doc.to_dict()["city"])
        except:
            history = []

    if request.method == "POST":
        city = request.form["city"]

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url).json()

        if res.get("cod") == 200:
            weather = {
                "city": res["name"],
                "temp": res["main"]["temp"],
                "desc": res["weather"][0]["description"],
                "icon": res["weather"][0]["icon"],
                "humidity": res["main"]["humidity"],
                "wind": res["wind"]["speed"]
            }

            # 🔥 Save only if Firebase works
            if firebase_enabled:
                try:
                    db.collection("history").add({"city": city})
                except:
                    pass

        else:
            weather = None

    return render_template("index.html", weather=weather, history=history)


# 📍 LOCATION ROUTE (NO FIREBASE HERE → SAFE)
@app.route("/location", methods=["POST"])
def location():
    data = request.get_json()
    lat = data["lat"]
    lon = data["lon"]

    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    res = requests.get(url).json()

    if res.get("cod") == 200:
        return jsonify({
            "city": res["name"],
            "temp": res["main"]["temp"],
            "desc": res["weather"][0]["description"],
            "icon": res["weather"][0]["icon"]
        })
    else:
        return jsonify({"error": "Location not found"})


if __name__ == "__main__":
    app.run(debug=True)
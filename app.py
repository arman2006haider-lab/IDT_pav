from flask import Flask, render_template, jsonify, request
import random
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# ── Sample data ──────────────────────────────────────────────────────────────

ANIMALS = [
    {"name": "Elephant", "kn": "ಆನೆ", "threat": "HIGH",   "emoji": "🐘", "color": "#ef4444"},
    {"name": "Gaur",     "kn": "ಕಾಡುಕೋಣ", "threat": "HIGH",   "emoji": "🐂", "color": "#f97316"},
    {"name": "Wild Boar","kn": "ಕಾಡು ಹಂದಿ", "threat": "MEDIUM", "emoji": "🐗", "color": "#eab308"},
    {"name": "Leopard",  "kn": "ಚಿರತೆ",  "threat": "HIGH",   "emoji": "🐆", "color": "#ef4444"},
    {"name": "Deer",     "kn": "ಜಿಂಕೆ",  "threat": "LOW",    "emoji": "🦌", "color": "#22c55e"},
    {"name": "Monkey",   "kn": "ಕೋತಿ",  "threat": "LOW",    "emoji": "🐒", "color": "#22c55e"},
]

THREAT_MATRIX = [
    {"animal": "Elephant", "kn": "ಆನೆ", "threat": "HIGH", "sms": "✅ Immediate", "buzzer": "✅ Loud Alarm", "light": "✅ Strobe Flash", "response": "Forest Dept. Alert"},
    {"animal": "Gaur",     "kn": "ಕಾಡುಕೋಣ", "threat": "HIGH", "sms": "✅ Immediate", "buzzer": "✅ Loud Alarm", "light": "✅ Strobe Flash", "response": "Forest Dept. Alert"},
    {"animal": "Leopard",  "kn": "ಚಿರತೆ",  "threat": "HIGH", "sms": "✅ Immediate", "buzzer": "✅ Loud Alarm", "light": "✅ Strobe Flash", "response": "Police + Forest"},
    {"animal": "Wild Boar","kn": "ಕಾಡು ಹಂದಿ", "threat": "MEDIUM","sms": "✅ Delayed 30s","buzzer": "✅ Moderate",  "light": "✅ Steady",       "response": "Farmer SMS only"},
    {"animal": "Deer",     "kn": "ಜಿಂಕೆ",  "threat": "LOW",  "sms": "📋 Log only",  "buzzer": "❌ Off",        "light": "⚠️ Dim",          "response": "Log & Monitor"},
    {"animal": "Monkey",   "kn": "ಕೋತಿ",  "threat": "LOW",  "sms": "📋 Log only",  "buzzer": "❌ Off",        "light": "❌ Off",           "response": "Log only"},
]

def make_detections(n=15):
    detections = []
    now = datetime.now()
    for i in range(n):
        animal = random.choice(ANIMALS)
        detections.append({
            "id": i + 1,
            "timestamp": (now - timedelta(minutes=i * 7)).strftime("%Y-%m-%d %H:%M:%S"),
            "animal": animal["name"],
            "animal_kn": animal["kn"],
            "threat": animal["threat"],
            "confidence": random.randint(78, 99),
            "sms_sent": animal["threat"] in ("HIGH", "MEDIUM"),
            "location": random.choice(["North Fence", "East Gate", "Crop Field A", "South Perimeter"]),
            "color": animal["color"],
            "emoji": animal["emoji"],
        })
    return detections

DETECTIONS = make_detections()

ESP32_SERIAL_LOG = [
    "[BOOT]  WildGuard v2.1 initializing...",
    "[WIFI]  Connecting to 'FarmNet_2G'...",
    "[WIFI]  Connected! IP: 192.168.1.42",
    "[PIR]   Sensor calibrated. Standby.",
    "[ULTRA] HC-SR04 distance: 847cm (clear)",
    "[CAM]   OV2640 init OK. Resolution: SVGA",
    "[HTTP]  Server: https://wildguard.cloud/api/detect",
    "[READY] System armed. Monitoring active.",
]

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    high = sum(1 for d in DETECTIONS if d["threat"] == "HIGH")
    sms  = sum(1 for d in DETECTIONS if d["sms_sent"])
    avg_conf = round(sum(d["confidence"] for d in DETECTIONS) / len(DETECTIONS))
    hourly = [random.randint(0, 8) for _ in range(24)]
    species_counts = {}
    for d in DETECTIONS:
        species_counts[d["animal"]] = species_counts.get(d["animal"], 0) + 1
    return render_template("dashboard.html",
        total=len(DETECTIONS), high=high, sms=sms, avg_conf=avg_conf,
        hourly=json.dumps(hourly),
        species_labels=json.dumps(list(species_counts.keys())),
        species_data=json.dumps(list(species_counts.values())),
        recent=DETECTIONS[:5],
    )

@app.route("/esp32")
def esp32():
    return render_template("esp32.html", log=ESP32_SERIAL_LOG)

@app.route("/detections")
def detections():
    return render_template("detections.html", detections=DETECTIONS)

@app.route("/alerts")
def alerts():
    return render_template("alerts.html", detections=DETECTIONS)

@app.route("/api-docs")
def api_docs():
    return render_template("api.html")

@app.route("/threat-matrix")
def threat_matrix():
    return render_template("threat_matrix.html", matrix=THREAT_MATRIX)

# ── API endpoints ─────────────────────────────────────────────────────────────

@app.route("/api/detect", methods=["POST"])
def api_detect():
    animal = random.choice(ANIMALS)
    conf   = random.randint(80, 99)
    gpio   = {"HIGH": {"buzzer": 1, "strobe": 1, "sms": 1},
              "MEDIUM": {"buzzer": 1, "strobe": 0, "sms": 1},
              "LOW": {"buzzer": 0, "strobe": 0, "sms": 0}}[animal["threat"]]
    return jsonify({
        "status": "ok",
        "animal": animal["name"],
        "threat_level": animal["threat"],
        "confidence": conf,
        "gpio_commands": gpio,
        "timestamp": datetime.now().isoformat(),
        "sms_dispatched": gpio["sms"] == 1,
    })

@app.route("/api/simulate")
def simulate():
    animal = random.choice(ANIMALS)
    conf = random.randint(80, 99)
    entry = {
        "id": len(DETECTIONS) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "animal": animal["name"],
        "animal_kn": animal["kn"],
        "threat": animal["threat"],
        "confidence": conf,
        "sms_sent": animal["threat"] in ("HIGH", "MEDIUM"),
        "location": random.choice(["North Fence", "East Gate", "Crop Field A", "South Perimeter"]),
        "color": animal["color"],
        "emoji": animal["emoji"],
    }
    DETECTIONS.insert(0, entry)
    return jsonify(entry)

@app.route("/api/esp32-status")
def esp32_status():
    return jsonify({
        "pir_triggered": random.choice([True, False]),
        "ultrasonic_cm": random.randint(80, 600),
        "wifi_rssi": random.randint(-75, -35),
        "gpio_buzzer": random.choice([0, 1]),
        "gpio_strobe": 0,
        "battery_pct": random.randint(60, 100),
        "uptime_s": random.randint(3600, 86400),
        "last_post_ms": random.randint(120, 450),
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)

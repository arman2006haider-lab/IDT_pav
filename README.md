# WildGuard — Wildlife Intrusion Alert System
### A Flask demo prototype for the Human-Wildlife Conflict Solution

## Run Locally

```bash
pip install flask
python app.py
# Open http://localhost:5000
```

## Pages
| Route | Description |
|---|---|
| `/` | Dashboard — metrics, architecture flow, charts |
| `/esp32` | Live ESP32 sensor readings + serial log |
| `/detections` | Full detection log with filter |
| `/alerts` | SMS templates + deterrent status |
| `/threat-matrix` | Animal → threat level → response table |
| `/api-docs` | FastAPI endpoint reference + live test |

## API Endpoints
- `POST /api/detect` — Main detection endpoint (ESP32 → Cloud)
- `GET /api/esp32-status` — Live sensor poll
- `GET /api/simulate` — Inject a random detection for demo

## Language Toggle
Click **EN / ಕನ್ನಡ** in the top-right to switch between English and Kannada.

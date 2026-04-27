# Quick Start — Verkada API Mock Server

Auto-generated mock server for **Verkada API v1.0.0**, running on port **9092**.

## Prerequisites

- Python 3.9+
- pip

## 1. Install dependencies

```bash
cd /Users/ankonduri/ClaudeCodeCustomSkills/mock-api-server/verkada-api
pip install -r requirements.txt
```

> `requirements.txt` includes: flask

## 2. Start the server

```bash
python mock_server.py
```

Expected output:

```
Mock server for "Verkada API" running on http://localhost:9092
 * Running on http://0.0.0.0:9092
```

## 3. Mocked endpoints

- `GET /cameras/v1/devices` — List all cameras in the organization
- `GET /cameras/v1/alerts` — List camera-triggered alert events
- `GET /alarms/v1/devices` — List alarm sensor devices

## Authentication

The mock server runs in **bypass mode** (`AUTH_ENFORCE = False`) by default. Set `AUTH_ENFORCE = True` in `mock_server.py` to enforce credentials.

| Scheme | Type | Header / Param | Mock credential | curl flag |
|--------|------|---------------|-----------------|----------|
| `ApiKey` | API Key (header) | `x-api-key` | `mock-apikey-key` | `-H 'x-api-key: mock-apikey-key'` |

```bash
curl -s 'http://localhost:9092/mock-auth-status' | python3 -m json.tool
```

## 4. Send queries

```bash
API_KEY="mock-apikey-key"
```

```bash
# GET /cameras/v1/devices — List all cameras (3 mock cameras across 2 sites)
curl -s 'http://localhost:9092/cameras/v1/devices' \
  -H "x-api-key: $API_KEY" | python3 -m json.tool
```

```bash
# GET /cameras/v1/alerts — Camera-triggered alert events
# Each alert contains camera_id — matches a camera in /cameras/v1/devices
curl -s 'http://localhost:9092/cameras/v1/alerts' \
  -H "x-api-key: $API_KEY" | python3 -m json.tool
```

```bash
# GET /alarms/v1/devices — Alarm sensor devices
# Devices with camera_id are associated with a camera (same camera_id as in /cameras/v1/devices)
curl -s 'http://localhost:9092/alarms/v1/devices' \
  -H "x-api-key: $API_KEY" | python3 -m json.tool
```

### Camera ↔ Alarm linkage

Verkada links cameras to alarms in two ways — both use `camera_id` as the join key:

| Relationship | How to join |
|---|---|
| Which camera triggered an alert? | `alerts[].camera_id` → `cameras[].camera_id` in `/cameras/v1/devices` |
| Which camera covers an alarm sensor zone? | `alarm_devices[].camera_id` → `cameras[].camera_id` in `/cameras/v1/devices` |

Mock data cross-reference:

| camera_id | camera_name | Alerts | Alarm sensors |
|---|---|---|---|
| `a1b2c3d4-0001-...` | Front Entrance | 1 (person_of_interest) | Main Entrance Door Sensor |
| `a1b2c3d4-0002-...` | Parking Lot North | 2 (motion, line_crossing) | Parking Lot Motion Sensor |
| `a1b2c3d4-0003-...` | Server Room Door | — | Server Room Glass Break (status: **alarm**) |

## 5. Override a response at runtime

Swap in any body or status code without restarting:

```bash
curl -s -X POST 'http://localhost:9092/mock-control' \
  -H 'Content-Type: application/json' \
  -d '{"key": "GET:/cameras/v1/devices", "response": {"error": "Service unavailable"}, "status": 503}'
```

## 6. Debug checklist

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `Connection refused` | Server not running | Run `python mock_server.py` |
| `Address already in use` | Port 9092 taken | Use `--port <other>` or `lsof -i :9092` to find the process |
| `401 Unauthorized` | `AUTH_ENFORCE=True` with wrong/missing credential | Send the `mock_value` from `AUTH_SCHEMES`, or set `AUTH_ENFORCE=False` |
| `404 Not Found` | Wrong path or base path missing | Check base path prefix — all routes start with `/` |
| `ModuleNotFoundError: flask` | Dependencies not installed | `pip install -r requirements.txt` |
| Unexpected response body | `MOCK_RESPONSES` override active | `POST /mock-control` with the correct key to reset, or restart |

## 7. Customise responses

- **Edit at startup**: modify the `body = ...` literal inside any route function in `mock_server.py`.
- **Edit the registry**: update `MOCK_RESPONSES` dict at the top of `mock_server.py`.
- **Edit at runtime**: `POST /mock-control` (no restart needed).
- **Toggle auth enforcement**: change `AUTH_ENFORCE = True/False` in `mock_server.py`.

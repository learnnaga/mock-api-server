# Quick Start — Crestron XiO Cloud API Mock Server

Auto-generated mock server for **Crestron XiO Cloud API v2.0.0**, running on port **9093**.

## Prerequisites

- Python 3.9+
- pip

## 1. Install dependencies

```bash
cd crestron-xio-cloud-api
pip install -r requirements.txt
```

> `requirements.txt` includes: flask

## 2. Start the server

```bash
python mock_server.py
```

Expected output:

```
Mock server for "Crestron XiO Cloud API" running on http://localhost:9093
 * Running on http://0.0.0.0:9093
```

## 3. Mocked endpoints

- `GET /api/v1/device/accountid/{accountid}/devices` — List all devices for an account
- `GET /api/v1/device/accountid/{accountid}/devicecid/{devicecid}/status` — Get full network status for a device (v1)
- `GET /api/v2/device/accountid/{accountid}/devicecid/{devicecid}/status` — Get full network status for a device (v2)
- `POST /api/v2/device/accountid/{accountid}/devicestatus` — Batch device status lookup
- `GET /api/v2/device/accountid/{accountId}/pageno/{pagenum}/pagesize/{pagesize}/status` — List device status (paginated)
- `GET /api/v2/device/accountid/{accountId}/devicemodel/{deviceModel}/pageno/{pagenum}/pagesize/{pagesize}/status` — List device status filtered by model (paginated)
- `GET /api/v1/group/accountid/{accountid}/groupid/{groupid}/devices` — List devices in a group
- `POST /api/v2/deviceclaim/accountid/{accountId}/macaddress/{macaddress}/serialnumber/{serialnumber}` — Claim a device by MAC address and serial number

## Authentication

The mock server runs in **bypass mode** (`AUTH_ENFORCE = False`) by default. Set `AUTH_ENFORCE = True` in `mock_server.py` to enforce credentials.

| Scheme | Type | Header / Param | Mock credential | curl flag |
|--------|------|---------------|-----------------|----------|
| `XiOSubscriptionKey` | API Key (header) | `XiO-subscription-key` | `mock-xiosubscriptionkey-key` | `-H 'XiO-subscription-key: mock-xiosubscriptionkey-key'` |

```bash
curl -s 'http://localhost:9093/mock-auth-status' | python3 -m json.tool
```

## 4. Send queries

# GET /api/v1/device/accountid/{accountid}/devices — List all devices for an account
curl -s 'http://localhost:9093/api/v1/device/accountid/1/devices' \
  -H 'XiO-subscription-key: mock-xiosubscriptionkey-key'

# GET /api/v1/device/accountid/{accountid}/devicecid/{devicecid}/status — Get full network status for a device (v1)
curl -s 'http://localhost:9093/api/v1/device/accountid/1/devicecid/1/status' \
  -H 'XiO-subscription-key: mock-xiosubscriptionkey-key'

# GET /api/v2/device/accountid/{accountid}/devicecid/{devicecid}/status — Get full network status for a device (v2)
curl -s 'http://localhost:9093/api/v2/device/accountid/1/devicecid/1/status' \
  -H 'XiO-subscription-key: mock-xiosubscriptionkey-key'

# POST /api/v2/device/accountid/{accountid}/devicestatus — Batch device status lookup
curl -s -X POST 'http://localhost:9093/api/v2/device/accountid/1/devicestatus' \
  -H 'XiO-subscription-key: mock-xiosubscriptionkey-key' \
  -H 'Content-Type: application/json' \
  -d '{
  "devices": [
    {
      "device-cid": "1234567890abcdef",
      "device-name": "Conference Room A - TSW-1070",
      "device-model": "TSW-1070",
      "device-category": "Touch Screen",
      "device-status": "online",
      "serial-number": "2107ABC0001234",
      "firmware-version": "2.004.0084",
      "firmware-date": "2024-03-15",
      "status-host-name": "TSW-1070-CONF-A",
      "status-domain-name": "corp.example.com",
      "nic-1-ip-address": "10.10.1.101",
      "nic-1-subnet-mask": "255.255.255.0",
      "nic-1-def-router": "10.10.1.1",
      "nic-1-mac-address": "00.11.22.aa.bb.01",
      "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
      "nic-2-ip-address": "",
      "nic-2-mac-address": "",
      "last-online-datetime": "2024-06-01T14:22:00Z",
      "room-id": "room-abc123",
      "room-name": "Conference Room A"
    }
  ]
}'

# GET /api/v2/device/accountid/{accountId}/pageno/{pagenum}/pagesize/{pagesize}/status — List device status (paginated)
curl -s 'http://localhost:9093/api/v2/device/accountid/1/pageno/1/pagesize/1/status' \
  -H 'XiO-subscription-key: mock-xiosubscriptionkey-key'

# GET /api/v2/device/accountid/{accountId}/devicemodel/{deviceModel}/pageno/{pagenum}/pagesize/{pagesize}/status — List device status filtered by model (paginated)
curl -s 'http://localhost:9093/api/v2/device/accountid/1/devicemodel/1/pageno/1/pagesize/1/status' \
  -H 'XiO-subscription-key: mock-xiosubscriptionkey-key'

# GET /api/v1/group/accountid/{accountid}/groupid/{groupid}/devices — List devices in a group
curl -s 'http://localhost:9093/api/v1/group/accountid/1/groupid/1/devices' \
  -H 'XiO-subscription-key: mock-xiosubscriptionkey-key'

# POST /api/v2/deviceclaim/accountid/{accountId}/macaddress/{macaddress}/serialnumber/{serialnumber} — Claim a device by MAC address and serial number
curl -s -X POST 'http://localhost:9093/api/v2/deviceclaim/accountid/1/macaddress/1/serialnumber/1' \
  -H 'XiO-subscription-key: mock-xiosubscriptionkey-key' \
  -H 'Content-Type: application/json' \
  -d '{
  "device-cid": "1234567890abcdef",
  "mac-address": "00.11.22.aa.bb.cc",
  "serial-number": "2107ABC0001234",
  "claim-status": "success",
  "claimed-at": "2024-06-01T10:00:00Z"
}'

## 5. Override a response at runtime

Swap in any body or status code without restarting:

```bash
curl -s -X POST 'http://localhost:9093/mock-control' \
  -H 'Content-Type: application/json' \
  -d '{"key": "GET:/api/v1/device/accountid/{accountid}/devices", "response": {"error": "Service unavailable"}, "status": 503}'
```

## 6. Debug checklist

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `Connection refused` | Server not running | Run `python mock_server.py` |
| `Address already in use` | Port 9093 taken | Use `--port <other>` or `lsof -i :9093` to find the process |
| `401 Unauthorized` | `AUTH_ENFORCE=True` with wrong/missing credential | Send the `mock_value` from `AUTH_SCHEMES`, or set `AUTH_ENFORCE=False` |
| `404 Not Found` | Wrong path or base path missing | Check base path prefix — all routes start with `/` |
| `ModuleNotFoundError: flask` | Dependencies not installed | `pip install -r requirements.txt` |
| Unexpected response body | `MOCK_RESPONSES` override active | `POST /mock-control` with the correct key to reset, or restart |

## 7. Customise responses

- **Edit at startup**: modify the `body = ...` literal inside any route function in `mock_server.py`.
- **Edit the registry**: update `MOCK_RESPONSES` dict at the top of `mock_server.py`.
- **Edit at runtime**: `POST /mock-control` (no restart needed).
- **Toggle auth enforcement**: change `AUTH_ENFORCE = True/False` in `mock_server.py`.

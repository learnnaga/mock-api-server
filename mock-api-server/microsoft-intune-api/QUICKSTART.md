# Quick Start — Microsoft Intune API Mock Server

Auto-generated mock server for **Microsoft Intune API v1.0.0**, running on port **9095**.

## Prerequisites

- Python 3.9+
- pip

## 1. Install dependencies

```bash
cd microsoft-intune-api
pip install -r requirements.txt
```

> `requirements.txt` includes: flask

## 2. Start the server

```bash
python mock_server.py
```

Expected output:

```
Mock server for "Microsoft Intune API" running on http://localhost:9095
 * Running on http://0.0.0.0:9095
```

## 3. Mocked endpoints

- `GET /v1.0/deviceManagement/managedDevices` — List all Intune-enrolled devices
- `GET /v1.0/deviceManagement/managedDevices/{managedDeviceId}` — Get a single managed device with full hardware detail
- `GET /v1.0/deviceManagement/deviceCompliancePolicies` — List device compliance policies
- `GET /v1.0/deviceManagement/deviceConfigurations` — List device configuration profiles
- `GET /v1.0/deviceManagement/managedDevices/{managedDeviceId}/deviceCompliancePolicyStates` — Get per-device compliance policy results

## Authentication — real two-step OAuth2 flow

This API uses OAuth2. The real client flow is:

1. **Step 1** — POST `client_id` + `client_secret` + `grant_type` to the identity provider → receive `access_token`
2. **Step 2** — Send `Authorization: Bearer <access_token>` with every API call

The mock server simulates **both steps**. The token endpoint is hosted locally at the same path as the real provider (host stripped), so client code only needs to change the base URL. Any `client_id` / `client_secret` is accepted.

### Step 1 — Acquire a mock token

```bash
# Scheme: IntuneOAuth2 (clientCredentials)
# Mirrors real token URL: https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token
TOKEN=$(curl -s -X POST 'http://localhost:9095/your-tenant-id/oauth2/v2.0/token' \
  -d 'client_id=<your-app-id>' \
  -d 'client_secret=<your-client-secret>' \
  -d 'grant_type=client_credentials' \
  -d 'scope=https://graph.microsoft.com/.default' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Token acquired: $TOKEN"
```

> The returned `access_token` is pre-wired to work with all mocked API endpoints below.

### Step 2 — Use `$TOKEN` in API calls

All curl examples in section 4 use `$TOKEN` from Step 1. Run Step 1 first in the same shell session.

Inspect the current auth config at any time:
```bash
curl -s 'http://localhost:9095/mock-auth-status' | python3 -m json.tool
```

**Bypass vs enforce mode:**

| `AUTH_ENFORCE` | Behaviour |
|---|---|
| `False` (default) | All requests pass; credentials are logged but not checked |
| `True` | Token from Step 1 required; wrong/missing token → `401` |

Toggle in `mock_server.py`: `AUTH_ENFORCE = True`

## 4. Send queries

# GET /v1.0/deviceManagement/managedDevices — List all Intune-enrolled devices
curl -s 'http://localhost:9095/v1.0/deviceManagement/managedDevices' \
  -H "Authorization: Bearer $TOKEN"

# GET /v1.0/deviceManagement/managedDevices/{managedDeviceId} — Get a single managed device with full hardware detail
curl -s 'http://localhost:9095/v1.0/deviceManagement/managedDevices/1' \
  -H "Authorization: Bearer $TOKEN"

# GET /v1.0/deviceManagement/deviceCompliancePolicies — List device compliance policies
curl -s 'http://localhost:9095/v1.0/deviceManagement/deviceCompliancePolicies' \
  -H "Authorization: Bearer $TOKEN"

# GET /v1.0/deviceManagement/deviceConfigurations — List device configuration profiles
curl -s 'http://localhost:9095/v1.0/deviceManagement/deviceConfigurations' \
  -H "Authorization: Bearer $TOKEN"

# GET /v1.0/deviceManagement/managedDevices/{managedDeviceId}/deviceCompliancePolicyStates — Get per-device compliance policy results
curl -s 'http://localhost:9095/v1.0/deviceManagement/managedDevices/1/deviceCompliancePolicyStates' \
  -H "Authorization: Bearer $TOKEN"

## 5. Override a response at runtime

Swap in any body or status code without restarting:

```bash
curl -s -X POST 'http://localhost:9095/mock-control' \
  -H 'Content-Type: application/json' \
  -d '{"key": "GET:/v1.0/deviceManagement/managedDevices", "response": {"error": "Service unavailable"}, "status": 503}'
```

## 6. Debug checklist

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `Connection refused` | Server not running | Run `python mock_server.py` |
| `Address already in use` | Port 9095 taken | Use `--port <other>` or `lsof -i :9095` to find the process |
| `401 Unauthorized` | `AUTH_ENFORCE=True` with wrong/missing credential | Send the `mock_value` from `AUTH_SCHEMES`, or set `AUTH_ENFORCE=False` |
| `404 Not Found` | Wrong path or base path missing | Check base path prefix — all routes start with `/` |
| `ModuleNotFoundError: flask` | Dependencies not installed | `pip install -r requirements.txt` |
| Unexpected response body | `MOCK_RESPONSES` override active | `POST /mock-control` with the correct key to reset, or restart |

## 7. Customise responses

- **Edit at startup**: modify the `body = ...` literal inside any route function in `mock_server.py`.
- **Edit the registry**: update `MOCK_RESPONSES` dict at the top of `mock_server.py`.
- **Edit at runtime**: `POST /mock-control` (no restart needed).
- **Toggle auth enforcement**: change `AUTH_ENFORCE = True/False` in `mock_server.py`.

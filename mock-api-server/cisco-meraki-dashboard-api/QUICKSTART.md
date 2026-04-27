# Quick Start — Cisco Meraki Dashboard API Mock Server

Auto-generated mock server for **Cisco Meraki Dashboard API v2.0.0**, running on port **9090**.

## Prerequisites

- Python 3.9+
- pip

## 1. Install dependencies

```bash
cd /Users/ankonduri/ClaudeCodeCustomSkills/mock-api-server/cisco-meraki-dashboard-api
pip install -r requirements.txt
```

> `requirements.txt` includes: flask

## 2. Start the server

```bash
python mock_server.py
```

Expected output:

```
Mock server for "Cisco Meraki Dashboard API" running on http://localhost:9090
 * Running on http://0.0.0.0:9090
```

## 3. Mocked endpoints

- `GET /api/v1/organizations` — List the organizations that the user has privileges on
- `GET /api/v1/organizations/{organizationId}/networks` — List the networks in an organization
- `GET /api/v1/organizations/{organizationId}/networks/{networkId}/clients` — List the clients on a network

## Authentication

This API uses API key authentication. The mock server runs in **enforce mode** (`AUTH_ENFORCE = True`) — the API key header is required on every request.

| Scheme | Type | Header | Mock credential | curl flag |
|--------|------|--------|-----------------|----------|
| `meraki_api_key` | API Key (header) | `X-Cisco-Meraki-API-Key` | `mock-meraki-api-key-key` | `-H 'X-Cisco-Meraki-API-Key: mock-meraki-api-key-key'` |

Check the current auth config at runtime:
```bash
curl -s 'http://localhost:9090/mock-auth-status' | python3 -m json.tool
```

> Set `AUTH_ENFORCE = False` in `mock_server.py` to switch to bypass mode (credentials logged but not checked).

## 4. Send queries

```bash
API_KEY="mock-meraki-api-key-key"
```

```bash
# GET /api/v1/organizations — List organizations (returns 2 orgs)
curl -s 'http://localhost:9090/api/v1/organizations' \
  -H "X-Cisco-Meraki-API-Key: $API_KEY" | python3 -m json.tool
```

```bash
# GET /api/v1/organizations/{organizationId}/networks — Networks for Acme Corp
curl -s 'http://localhost:9090/api/v1/organizations/12345678901234567/networks' \
  -H "X-Cisco-Meraki-API-Key: $API_KEY" | python3 -m json.tool
```

```bash
# GET /api/v1/organizations/{organizationId}/networks/{networkId}/clients — Clients on Main Office network
curl -s 'http://localhost:9090/api/v1/organizations/12345678901234567/networks/N_12345678901234567/clients' \
  -H "X-Cisco-Meraki-API-Key: $API_KEY" | python3 -m json.tool
```

### Mock data reference

| Endpoint | Key fields in response |
|----------|----------------------|
| `GET /organizations` | 2 orgs: `Acme Corp` (id `12345678901234567`, NA region), `Globex Industries` (id `98765432109876543`, Europe region) |
| `GET /organizations/{id}/networks` | 1 network: `Main Office` (id `N_12345678901234567`), appliance + switch + wireless |
| `GET /organizations/{id}/networks/{id}/clients` | 3 clients: `John-MacBook-Pro` (Online, WiFi), `Finance-PC-01` (Online, Wired), `Conference-Room-TV` (Offline, WiFi) |

## 5. Override a response at runtime

Swap in any body or status code without restarting:

```bash
curl -s -X POST 'http://localhost:9090/mock-control' \
  -H 'Content-Type: application/json' \
  -d '{"key": "GET:/organizations", "response": {"error": "Service unavailable"}, "status": 503}'
```

## 6. Debug checklist

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `Connection refused` | Server not running | Run `python mock_server.py` |
| `Address already in use` | Port 9090 taken | Use `--port <other>` or `lsof -i :9090` to find the process |
| `401 Unauthorized` | Missing or wrong API key | Send `-H 'X-Cisco-Meraki-API-Key: mock-meraki-api-key-key'`, or set `AUTH_ENFORCE=False` |
| `404 Not Found` | Wrong path or base path missing | All routes start with `/api/v1` |
| `ModuleNotFoundError: flask` | Dependencies not installed | `pip install -r requirements.txt` |
| Unexpected response body | `MOCK_RESPONSES` override active | `POST /mock-control` with the correct key to reset, or restart |

## 7. Customise responses

- **Edit at startup**: modify the `body = ...` literal inside any route function in `mock_server.py`.
- **Edit the registry**: update `MOCK_RESPONSES` dict at the top of `mock_server.py`.
- **Edit at runtime**: `POST /mock-control` (no restart needed).
- **Toggle auth enforcement**: change `AUTH_ENFORCE = True/False` in `mock_server.py`.

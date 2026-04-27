# Mock API Server — Claude Code Usage Guide

This skill reads an OpenAPI 2.x or 3.x spec and generates a **self-contained Flask mock server** with auth middleware, schema-driven responses, and a ready-to-run QUICKSTART guide.

---

## Generator CLI Reference

Claude runs `generate_mock_server.py` under the hood. You can also invoke it directly.

```
python generate_mock_server.py <spec_file> [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `spec` | *(required)* | Path to spec file — `.json`, `.yaml`, or `.yml` |
| `--endpoints METHOD:/path ...` | all endpoints | Whitelist specific endpoints to mock |
| `--port <number>` | `8080` | HTTP port for the mock server |
| `--out-dir <path>` | spec file directory | Parent directory for the generated folder |
| `--run` | off | Generate folder **and** start the server immediately |
| `--smoke-test` | off | Generate → start → probe every endpoint → report PASS/FAIL → exit |
| `--data-config <path>` | auto-detected | Path to `mock-data-config.yaml` (auto-found in generator/spec/cwd if omitted) |

### Examples

```bash
# Mock all endpoints, default port
python generate_mock_server.py ./openapi.yaml

# Mock two specific endpoints on port 9090
python generate_mock_server.py ./openapi.yaml \
  --endpoints GET:/users POST:/users \
  --port 9090

# Generate into a specific folder and start immediately
python generate_mock_server.py ./openapi.yaml \
  --out-dir ~/mocks \
  --port 3000 \
  --run

# CI pipeline: generate + test + exit with code 0/1
python generate_mock_server.py ./openapi.yaml --smoke-test
```

---

## Runtime Controls (no restart needed)

### Toggle auth enforcement
Edit `mock_server.py` and change:
```python
AUTH_ENFORCE = True   # require credentials
AUTH_ENFORCE = False  # log only (default)
```

### Override any response on the fly
```bash
curl -s -X POST 'http://localhost:8080/mock-control' \
  -H 'Content-Type: application/json' \
  -d '{"key": "GET:/users", "response": {"error": "down"}, "status": 503}'
```

Reset by restarting the server or POSTing the original body back.

### Inspect current auth config
```bash
curl -s 'http://localhost:8080/mock-auth-status' | python3 -m json.tool
```

---

## Claude Prompts

### Basic generation

> Generate a mock server from `./openapi.yaml`

> Create a mock from `petstore.json` on port 9090

> Mock all endpoints in `api-spec.yaml` and put the output in `~/mocks`

---

### Selective endpoints

> Generate a mock for `GET:/users` and `POST:/users` from `openapi.yaml` on port 3000

> From `meraki.json` mock only `GET:/organizations` and `GET:/organizations/{id}/networks`

> Mock the machines endpoint and the vulnerabilities endpoint from `defender.json`

---

### Start and test immediately

> Generate a mock server from `openapi.yaml` and start it

> Generate and run smoke-test queries against `petstore.yaml` on port 9091

> Generate a mock from `spec.json`, start it, and send a test request to every endpoint

---

### Real OAuth2 / Azure AD auth flow

> Generate a mock for `defender.json` — I want the full two-step OAuth2 flow so I can test my client without changing code

> Mock `api-spec.yaml` and show me how to get a token first, then call the API

> My client uses `client_credentials` grant against Azure AD. Mock `spec.json` so I can point my client at localhost

---

### Inline spec (no file)

> Here is my OpenAPI spec: [paste YAML or JSON]. Mock `GET:/products` and `GET:/products/{id}` on port 8080 and start it.

---

### Updating an existing mock

> Add `DELETE:/users/{id}` to the existing mock for `openapi.yaml`

> The port needs to change from 9090 to 3000 — regenerate the mock

> I changed the `mock_value` for the API key in `mock_server.py` — update QUICKSTART.md to match

---

### Debugging

> The mock is returning 404 — help me debug it

> I'm getting 401 even in bypass mode — check the auth config

> Run the smoke test again and show me which endpoints are failing

---

## Output Structure

Each spec gets its own isolated folder named after `info.title`:

```
<api-title>/
├── mock_server.py    # Flask server — routes, auth middleware, /mock-control
├── requirements.txt  # flask>=3.0  (+ pyyaml for YAML specs)
└── QUICKSTART.md     # install → start → auth table → curl examples → debug guide
```

Multiple specs can run side-by-side on different ports without conflicts.

---

## OAuth2 Two-Step Flow (auto-generated)

When a spec declares an `oauth2` or `openIdConnect` scheme, the generator **always** emits a mock token endpoint at the same path as the real identity provider (host stripped). Your client code works against the mock with only a base-URL change.

```bash
# Step 1 — get a token (any client_id / client_secret accepted)
TOKEN=$(curl -s -X POST \
  'http://localhost:8080/{tenant-id}/oauth2/v2.0/token' \
  -d 'client_id=my-app&client_secret=any&grant_type=client_credentials' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Step 2 — call the API
curl -s 'http://localhost:8080/api/machines' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## Running Multiple Mocks Simultaneously

Each generated folder is independent — you can run as many mock servers as you like on the same host, one per port.

```bash
# Terminal 1 — Meraki on 9090
cd cisco-meraki-dashboard-api && python mock_server.py

# Terminal 2 — MS Defender on 9091
cd microsoft-defender-for-endpoint-api && python mock_server.py

# Terminal 3 — Petstore on 9092
cd swagger-petstore-openapi-3-0 && python mock_server.py
```

The only requirement: **each server must use a different port**. If two mocks share the same port the second one will fail with `Address already in use`.

### Change the port on an existing mock

**Quick edit** — update the last line of `mock_server.py`:
```python
app.run(host='0.0.0.0', port=9091, debug=True)
```

**Regenerate** — pass a different port to the generator (rewrites all three files):
```bash
python generate_mock_server.py spec.json --port 9091 --out-dir /path/to/output
```

> Regeneration overwrites any manual edits in `mock_server.py`. Use the quick edit if you've customised response bodies or `mock_value`s.

### Claude prompts for multi-port setups

> Regenerate the MS Defender mock on port 9091 so I can run it alongside the Meraki mock on 9090

> Change the Petstore mock to port 9092 without regenerating

> What port is each of my mocks running on?

---

## Unified Portal (Swagger UI for all mocks)

`mock_portal.py` is a single server (port 8888) that provides Swagger UI for every registered mock — no configuration needed beyond starting it.

### Prerequisites

```bash
pip install flask requests
```

### Start the portal + all mocks

```bash
# Terminal 1 — Meraki
cd cisco-meraki-dashboard-api && python mock_server.py

# Terminal 2 — MS Defender
cd microsoft-defender-for-endpoint-api && python mock_server.py

# Terminal 3 — Verkada
cd verkada-api && python mock_server.py

# Terminal 4 — Portal
cd /path/to/mock-api-server && python mock_portal.py
```

Then open **http://localhost:8888** — you'll see a card per mock with live status dots.

### What the portal does

| URL | What it shows |
|-----|---------------|
| `http://localhost:8888/` | Homepage — card per mock, live up/down status, auth badges |
| `http://localhost:8888/swagger/<slug>` | Swagger UI for that mock — auth pre-filled, Try It Out enabled |
| `http://localhost:8888/api/spec/<slug>` | Rewritten OpenAPI spec (servers[] → proxy path) |
| `http://localhost:8888/proxy/<slug>/...` | Transparent proxy to the actual mock server |
| `http://localhost:8888/api/status` | JSON liveness check for all mocks |

### How "Try It Out" works

The portal rewrites each spec's `servers[]` URL to point through the proxy before serving it to Swagger UI. When you click "Execute" in Swagger UI, the request goes:

```
Swagger UI  →  /proxy/<slug>/api/v1/...  →  mock server :port  →  response
```

Auth credentials (API keys) are **auto-filled** in the Authorize dialog when the Swagger UI page loads — just click Execute immediately.

### OAuth2 two-step (MS Defender)

The portal also rewrites the OAuth2 `tokenUrl` through the proxy. To test the full flow in Swagger UI:

1. Click **Authorize** → fill `client_id`, `client_secret`, click **Authorize** — the portal proxies the token request to the mock token endpoint
2. Swagger UI stores the returned Bearer token and sends it on every request

### Adding a new mock to the portal

When you generate a new mock with the generator, `portal-config.json` is **automatically updated**. Just restart the portal to pick it up.

To add a manually-created server, edit `portal-config.json`:

```json
{
  "mocks": [
    {
      "slug":    "my-api",
      "title":   "My API",
      "version": "1.0.0",
      "port":    9093,
      "dir":     "my-api",
      "auth_enforce": false,
      "auth_schemes": [
        { "name": "ApiKey", "type": "apiKey", "in": "header", "param_name": "x-api-key", "mock_value": "my-key" }
      ]
    }
  ]
}
```

Then place your `openapi.json` in `my-api/openapi.json` and restart the portal.

### Claude prompts for portal

> Start the portal and all mock servers

> Open Swagger UI for the Meraki mock

> Why is the Defender mock showing as offline in the portal?

> Add the newly generated petstore mock to the portal

---

---

## Data Configuration (mock-data-config.yaml)

Control how many items each endpoint returns and override specific fields — without regenerating.

### Format

```yaml
<api-slug>:          # slugified info.title, e.g. cisco-meraki-dashboard-api
  endpoints:
    /path/to/endpoint:
      count: 5                    # number of items
      fields:
        name: "Item {index}"      # {index} → 0-based item number
        status: active
      nested:                     # for responses like {"value": [...]}
        array_key: value
        count_key: "@odata.count"
```

The file is **auto-discovered** — place it next to `generate_mock_server.py` and it's picked up automatically.

### Claude prompts for data config

> Generate a mock for `meraki.json` — I want 10 organizations and 5 networks each

> Regenerate the Defender mock with 20 machines named "Device {index}" and healthStatus Active

> How do I configure the Verkada mock to return 15 cameras?

---

## Tips

- **Start with `AUTH_ENFORCE = False`** (the default) while building your client. Switch to `True` only when testing the auth flow end-to-end.
- **Inline `example` fields** in your spec produce richer mock data — the generator uses them verbatim.
- **Use `--smoke-test` in CI** — exit code `0` means all endpoints passed, `1` means at least one failed.
- **Use `/mock-control` for error injection** — simulate 429, 503, or custom payloads without touching code.

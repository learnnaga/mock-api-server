# Using the Mock API Server in VS Code (without Claude Code)

This guide covers three ways to use the mock API generator in VS Code. All three work without installing Claude Code.

---

## Option A — Standalone (no AI at all)

The generator is a plain Python script. You can drive it entirely from the VS Code integrated terminal.

### 1. Prerequisites

```bash
python --version     # must be 3.9+
pip install flask pyyaml
```

### 2. Generate a mock server

```bash
cd mock-api-server

# From a local spec file
python generate_mock_server.py path/to/openapi.json --port 9090

# With Kubernetes artifacts
python generate_mock_server.py path/to/openapi.json --port 9090 \
    --k8s --ingress-path /myapi

# Only add Helm chart to an already-existing mock (won't touch mock_server.py)
python generate_mock_server.py path/to/openapi.json --port 9090 \
    --k8s-only --ingress-path /myapi
```

All flags:

| Flag | Default | Description |
|------|---------|-------------|
| `--port` | `8080` | Port Flask listens on |
| `--endpoints` | all | Space-separated list, e.g. `GET:/users POST:/users` |
| `--out-dir` | spec file directory | Parent directory for the generated folder |
| `--k8s` | off | Also generate `Dockerfile` + `helm/<chart>/` |
| `--k8s-only` | off | Generate **only** `Dockerfile` + `helm/<chart>/` — leaves `mock_server.py` untouched |
| `--ingress-path` | `/<api-slug>` | Ingress prefix, e.g. `/defender` |
| `--ingress-class` | `nginx` | Ingress class name |
| `--data-config` | auto | Path to `mock-data-config.yaml` |
| `--run` | off | Start the server immediately after generating |
| `--smoke-test` | off | Generate → start → probe all routes → exit |

### 3. Start the generated mock

```bash
cd <generated-folder>/        # e.g. cisco-meraki-dashboard-api/
pip install -r requirements.txt
python mock_server.py
```

The terminal will show `Running on http://0.0.0.0:<port>`.

### 4. Open QUICKSTART.md for ready-made curl examples

Every generated folder includes `QUICKSTART.md` with:
- Install steps
- Auth table (credentials, headers)
- `curl` examples for every endpoint
- Runtime override recipe

Open it in VS Code with `Ctrl+Shift+V` (Preview) for nicely rendered markdown.

### 5. Start the unified portal (optional)

```bash
python mock_portal.py
# Open http://localhost:8888 in your browser
# Swagger UI for every mock, with auth pre-filled and Try It Out enabled
```

---

## Option B — AI-assisted via Cline extension (VS Code + Claude API key)

[Cline](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev) is a VS Code extension that gives Claude full file-system and terminal access inside your editor, similar to Claude Code.

### 1. Install Cline

- Open VS Code Extensions (`Ctrl+Shift+X`)
- Search for **Cline** and install it

### 2. Configure your Anthropic API key

- Open Cline settings (click the Cline icon in the sidebar → gear icon)
- Set **API Provider** to `Anthropic`
- Paste your API key from [console.anthropic.com](https://console.anthropic.com)
- Set **Model** to `claude-sonnet-4-6` (recommended) or `claude-opus-4-7`

### 3. Point Cline at this project

Open this repo folder in VS Code. Cline automatically reads files in your workspace. The `SKILL.md` file in this folder documents exactly what the generator can do — Cline will use it as context.

### 4. Use the same natural-language prompts as Claude Code

In the Cline chat panel, use prompts like:

> "Read `SKILL.md` in this folder, then generate a mock server from `openapi.json` on port 9090 with a Helm chart for ingress path `/myapi`."

> "The mock in `microsoft-defender-for-endpoint-api/` was hand-edited. Add a Helm chart and Dockerfile for it on port 9090 with ingress path `/defender` — do not touch `mock_server.py`."

> "Start all six mock servers in the background and then open the portal."

> "Run a smoke test against the Meraki mock on port 9090."

Cline can read `SKILL.md`, run terminal commands, edit files, and report results — the same workflow as Claude Code.

### 5. Differences from Claude Code

| | Claude Code | Cline |
|--|-------------|-------|
| Install | `npm install -g @anthropic-ai/claude-code` | VS Code marketplace |
| Invocation | Terminal CLI (`claude`) | VS Code sidebar panel |
| Skill loading | Reads `SKILL.md` automatically | Must be mentioned in the first prompt |
| Context | Full project context by default | Ask it to read specific files if needed |
| Cost | Subscription or API key | Anthropic API key (pay-per-token) |

---

## Option C — Claude.ai web + VS Code terminal (copy-paste workflow)

No extensions or API keys required beyond a Claude.ai account.

### 1. Open two windows side by side

- Left: VS Code with this project open
- Right: [claude.ai](https://claude.ai) in a browser

### 2. Give Claude the skill context

In Claude.ai, paste the contents of `SKILL.md` at the start of a new conversation:

> "Here is a skill description for a mock API server generator. I want to use this to generate mocks. [paste contents of SKILL.md]"

### 3. Ask Claude to write the command for you

> "I have an OpenAPI spec at `./my-api/openapi.json`. What command should I run to generate a mock server on port 9090 with a Helm chart for ingress path `/myapi`?"

Claude will produce the exact `python generate_mock_server.py ...` command.

### 4. Paste and run in the VS Code terminal

Copy the command, paste it in the VS Code integrated terminal (`Ctrl+\``), and run it.

### 5. Ask Claude to help interpret output or debug

If a mock fails to start, paste the error into Claude.ai:

> "The mock server gave this error: [paste]. How do I fix it?"

---

## Working with the pre-built mocks

The repo includes six ready-made mock servers. Start any of them directly — no generation step needed.

```bash
# Meraki
cd cisco-meraki-dashboard-api
pip install -r requirements.txt
python mock_server.py &

# Defender
cd microsoft-defender-for-endpoint-api
pip install -r requirements.txt
python mock_server.py &

# Entra ID
cd microsoft-entra-id-api
pip install -r requirements.txt
python mock_server.py &

# Intune
cd microsoft-intune-api
pip install -r requirements.txt
python mock_server.py &

# Verkada
cd verkada-api
pip install -r requirements.txt
python mock_server.py &

# Crestron
cd crestron-xio-cloud-api
pip install -r requirements.txt
python mock_server.py &
```

Check they are all running:
```bash
for port in 9090 9091 9092 9093 9094 9095; do
    curl -s http://localhost:$port/mock-auth-status | python3 -m json.tool | grep auth_enforce \
    && echo "  → port $port OK" || echo "  → port $port NOT RUNNING"
done
```

---

## Customising a mock without regenerating

All mocks are plain Python — edit `mock_server.py` directly in VS Code.

### Change a response body

Find the `MOCK_RESPONSES` dict near the top of `mock_server.py`:
```python
MOCK_RESPONSES = {
    "GET /api/machines": { ... }   # edit this dict
}
```

Or inject at runtime without editing the file (server must be running):
```bash
curl -s -X POST http://localhost:9091/mock-control \
  -H "Content-Type: application/json" \
  -d '{"route": "GET /api/machines", "body": {"value": [], "@odata.count": 0}}'
```

### Toggle auth enforcement

In `mock_server.py`, find:
```python
AUTH_ENFORCE = False   # change to True to require credentials
```

### Add a new route

In `mock_server.py`, add a Flask route after the existing ones:
```python
@app.route("/api/my-new-endpoint", methods=["GET"])
def my_new_endpoint(**kwargs):
    return jsonify({"data": "hello"})
```

---

## VS Code tips

- **Split terminal**: `Ctrl+Shift+5` — run multiple mocks side by side.
- **Preview QUICKSTART.md**: Right-click the file → "Open Preview" for formatted curl examples.
- **Restart Defender mock quickly**: `lsof -ti :9091 | xargs kill -9 && python microsoft-defender-for-endpoint-api/mock_server.py &`
- **REST Client extension**: Install [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) and create `.http` files with the curl examples from QUICKSTART.md — run requests with one click without leaving VS Code.

### Sample `.http` file for Defender mock

```http
### Get all machines (no auth)
GET http://localhost:9091/api/machines

### Get token
# @name token
POST http://localhost:9091/abc123/oauth2/v2.0/token
Content-Type: application/x-www-form-urlencoded

client_id=my-app&client_secret=my-secret&grant_type=client_credentials&scope=https://api.securitycenter.microsoft.com/.default

### Get machines with auth
GET http://localhost:9091/api/machines
Authorization: Bearer {{token.response.body.access_token}}

### Get machine alerts
GET http://localhost:9091/api/machines/machine-001/alerts
Authorization: Bearer {{token.response.body.access_token}}
```

---

## Sharing this repo with your team

1. **Push to GitHub/GitLab** — the repo is self-contained; team members clone it and start any mock immediately.
2. **Each mock has its own `requirements.txt`** — `pip install -r requirements.txt` inside the mock folder is the only setup step.
3. **No secrets in the repo** — all mock credentials are fake values defined in `mock_server.py`; no `.env` files needed.
4. **Point teammates at this file** (`VSCODE_USAGE.md`) for onboarding — they can use Option A (standalone) without any Claude access.
5. **Helm charts** are in `<mock>/helm/<chart>/` — deploy directly to any cluster with `helm install`.

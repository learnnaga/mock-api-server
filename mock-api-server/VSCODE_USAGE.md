# Using the Mock API Server in VS Code (without Claude Code)

This guide covers how to use the mock API generator in VS Code across different setups — from no AI at all, to GitHub Copilot, to a dedicated Claude API key. **No Claude Code installation is required for any of these.**

### Which option is right for you?

| Your setup | Best option |
|-----------|-------------|
| No AI tools, just VS Code | [Option A — Standalone](#option-a--standalone-no-ai-at-all) — run the Python script directly |
| GitHub Copilot (free with GitHub Education or paid) | [Option B — GitHub Copilot](#option-b--github-copilot-no-api-key-needed) — context loads automatically via `.github/copilot-instructions.md` |
| Cursor, Continue.dev, or another AI editor | [Option B — Other AI editors](#other-ai-editors-cursor-continuedev) — similar file-reference approach |

> **Note on `SKILL.md` and `@skill`:** `SKILL.md` is a Claude Code-specific concept — Claude Code reads it automatically when you open this project. In VS Code there is no `@skill` command. The equivalent for GitHub Copilot is `.github/copilot-instructions.md`, which Copilot reads automatically for every conversation in the repo — no manual loading needed. See [Using this skill with GitHub Copilot](#using-this-skill-with-github-copilot-githubcopilot-instructionsmd) for setup.

---

## Creating a new mock server — example prompts

Before diving into setup options, here are the kinds of prompts you can give to **any AI assistant** (GitHub Copilot, Claude.ai, Cline, Cursor, etc.) to work with this toolkit. The AI tells you what command to run — you paste it in the VS Code terminal. The examples use Jamf Pro and Zoom because their OpenAPI specs are publicly available.

**Important:** Always start your AI conversation by loading the context file:
- GitHub Copilot: type `#file:SKILL.md` then your prompt
- Cursor: type `@SKILL.md` then your prompt  
- Claude.ai web / ChatGPT: paste the contents of `SKILL.md` first
- Cline / Continue.dev: start with "Read `SKILL.md` first, then..."

This tells the AI what the generator can do so its responses are accurate.

### Getting a spec file

Most enterprise APIs publish an OpenAPI spec. Download it first:

```bash
# Jamf Pro (download from Jamf Developer Portal or your Jamf instance)
# https://developer.jamf.com/jamf-pro/docs — download the YAML spec

# Zoom (public spec on GitHub)
curl -L https://raw.githubusercontent.com/zoom/zoom-api-spec/main/openapi.yaml \
  -o zoom-openapi.yaml
```

If you cannot find a public spec, paste the API documentation into Claude and ask it to write one for you (see prompt examples below).

---

### Jamf Pro — prompt examples

**Generate a mock for the most useful Jamf endpoints:**
> "Generate a mock server from `jamf-openapi.yaml` on port 9096. Focus on these endpoints: `GET:/api/v1/computers-inventory`, `GET:/api/v1/computers-inventory/{id}`, `GET:/api/v1/mobile-devices`, `GET:/api/v1/policies`, `GET:/api/v1/categories`. Use ingress path `/jamf`."

**Ask Claude to write the spec if you don't have one:**
> "I don't have an OpenAPI spec for Jamf Pro. Using the Jamf Pro API documentation at https://developer.jamf.com/jamf-pro/reference, write an OpenAPI 3.0 spec for these 5 endpoints and save it as `jamf-openapi.json`: computers inventory list, single computer detail, mobile devices list, policies list, categories list. Then generate a mock server from it on port 9096."

**Generate with realistic device data:**
> "Generate a mock for `jamf-openapi.json` on port 9096. The computers inventory endpoint should return 5 computers with realistic macOS device names like `MacBook-Pro-Alice`, serial numbers, IP addresses, and macOS versions. Add it to `mock-data-config.yaml`."

**Add a Helm chart after the mock already exists:**
> "The Jamf mock in `jamf-pro-api/` was hand-edited. Add a Helm chart and Dockerfile for it on port 9090 with ingress path `/jamf` — do not touch `mock_server.py`."

**Example expected output — Jamf computers inventory (`GET /api/v1/computers-inventory`):**
```json
{
  "totalCount": 5,
  "results": [
    {
      "id": "1",
      "udid": "550e8400-e29b-41d4-a716-446655440001",
      "general": {
        "name": "MacBook-Pro-Alice",
        "serialNumber": "C02XG2JHJGH6",
        "ipAddress": "192.168.1.101",
        "lastContactTime": "2024-03-15T10:30:00Z",
        "osVersion": "14.3.1"
      },
      "hardware": {
        "model": "MacBook Pro (16-inch, 2023)",
        "processorType": "Apple M3 Pro"
      }
    }
  ]
}
```

---

### Zoom — prompt examples

**Generate a mock for core Zoom meeting endpoints:**
> "Generate a mock server from `zoom-openapi.yaml` on port 9097. Mock these endpoints: `GET:/users`, `GET:/users/{userId}`, `GET:/users/{userId}/meetings`, `GET:/meetings/{meetingId}`, `GET:/meetings/{meetingId}/participants`. Use ingress path `/zoom`."

**Ask Claude to write the spec from documentation:**
> "Write an OpenAPI 3.0 spec for the Zoom Meetings API covering: list users, get user detail, list meetings for a user, get meeting detail, list meeting participants. Auth is OAuth2 bearer token. Save as `zoom-openapi.json` then generate a mock on port 9097."

**Generate with realistic meeting data:**
> "Generate a mock for `zoom-openapi.json` on port 9097. The users endpoint should return 4 users with Zoom-style email addresses and display names. The meetings endpoint should return 3 meetings with realistic topics like `Weekly Standup`, `Product Review`, `Customer Call`. Use `mock-data-config.yaml` to configure this."

**Generate with Kubernetes artifacts:**
> "Generate a mock from `zoom-openapi.yaml` on port 9090 with a Helm chart. Use `/zoom` as the ingress path. The external URL for listing users should be `http://mock.local/zoom/users`."

**Example expected output — Zoom users (`GET /users`):**
```json
{
  "page_count": 1,
  "page_number": 1,
  "page_size": 30,
  "total_records": 4,
  "users": [
    {
      "id": "KdYKjnIMT7KM4fCOmh-TrA",
      "first_name": "Alice",
      "last_name": "Johnson",
      "email": "alice.johnson@company.com",
      "type": 2,
      "status": "active",
      "dept": "Engineering",
      "created_at": "2022-01-15T09:00:00Z",
      "timezone": "America/New_York"
    }
  ]
}
```

---

### General prompts that work for any API

**From a spec file:**
> "Generate a mock server from `[spec-file]` on port [port]. Show me what endpoints are available and ask which ones I want to include."

**From API documentation (no spec file):**
> "Here is the API documentation for [API name]: [paste or link]. Write an OpenAPI 3.0 spec for the top 5 most useful endpoints and generate a mock server from it on port [port]."

**Smoke test after generating:**
> "Generate a mock from `[spec-file]` on port [port] and immediately run smoke tests to verify all endpoints return 200."

**Generate multiple mocks for a cluster:**
> "Generate mocks for Jamf (`jamf-openapi.json`) on port 9090 and Zoom (`zoom-openapi.yaml`) on port 9090, both with Helm charts — use `/jamf` and `/zoom` as ingress paths. All K8s services use port 9090."

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

## Option B — GitHub Copilot (no API key needed)

GitHub Copilot is the most common AI tool in VS Code — available free with GitHub Education or as a paid GitHub subscription. No separate API key required.

### 1. Open Copilot Chat

Click the Copilot icon in the VS Code sidebar, or press `Ctrl+Alt+I`.

### 2. Load SKILL.md as context

Copilot does not auto-read project files. Use the `#file:` reference to attach `SKILL.md` to your message:

```
#file:SKILL.md Generate a mock server from jamf-openapi.json on port 9096 with ingress path /jamf.
Tell me what command to run.
```

Copilot reads the file contents and uses it to understand what the generator supports.

### 3. Run the command Copilot gives you

Copilot will output the exact `python generate_mock_server.py ...` command. Paste it in the VS Code integrated terminal (`Ctrl+\``) and run it.

### 4. Example prompts for Copilot Chat

```
#file:SKILL.md What endpoints does the Meraki mock expose and how do I start it?
```

```
#file:SKILL.md I want to add a Helm chart to the existing Defender mock without
touching mock_server.py. Give me the exact command.
```

```
#file:SKILL.md The Zoom API mock returned a 404. Here is the error: [paste].
What is wrong and how do I fix it?
```

```
#file:SKILL.md Write an OpenAPI 3.0 spec for these 5 Jamf Pro endpoints:
computers inventory list, single computer detail, mobile devices list,
policies list, categories list. I will save it as jamf-openapi.json.
```

### 5. Copilot model options

GitHub Copilot Chat lets you switch models (GPT-4o, Claude Sonnet, Gemini, etc.) from the model picker in the chat panel. Any of them work — attach `#file:SKILL.md` the same way regardless of which model is selected.

---

### Other AI editors (Cursor, Continue.dev)

The same approach works in other AI-enabled editors — the file reference syntax differs:

| Editor / Tool | How to load SKILL.md context |
|--------------|------------------------------|
| **GitHub Copilot** | Automatic via `.github/copilot-instructions.md` (see below), or `#file:SKILL.md` per message |
| **Cursor** | `@SKILL.md` at the start of your message |
| **Continue.dev** | `@file SKILL.md` at the start of your message |

None of these tools have a built-in `@skill` command — you reference the file manually for the first message in a session. After that, the AI keeps it in context for the rest of the conversation.

---

## Using this skill with GitHub Copilot — `.github/copilot-instructions.md`

GitHub Copilot supports a special file that it reads **automatically** for every chat conversation in the repo — no `#file:` needed. This is the VS Code equivalent of how Claude Code reads `SKILL.md`.

### How it works

Create `.github/copilot-instructions.md` in the repo. Copilot loads it silently as background context for every Copilot Chat message in this workspace. You do not need to reference it — it is always active.

This repo already has one set up. It tells Copilot:
- What `generate_mock_server.py` does and what flags it accepts
- That it should always give you the exact terminal command to run
- The port and ingress conventions for this project

### Setup (already done in this repo)

```
mock-api-server/
└── .github/
    └── copilot-instructions.md   ← Copilot reads this automatically
```

### What Copilot can do with this context

Once the instructions file is present, Copilot Chat answers mock-server questions correctly without any preamble:

```
Generate a mock from jamf-openapi.json on port 9096 with ingress path /jamf
```

```
Add a Helm chart to the Defender mock on port 9090 — do not touch mock_server.py
```

```
The Meraki mock returns 404. Error: [paste]. What is wrong?
```

```
Write an OpenAPI spec for these 5 Jamf endpoints and tell me how to generate a mock from it
```

Copilot gives you the exact command. Paste it in the VS Code terminal and run it.

### Limitations vs Claude Code

| | Claude Code | GitHub Copilot + instructions |
|--|-------------|-------------------------------|
| Context loading | Automatic (reads `SKILL.md`) | Automatic (reads `.github/copilot-instructions.md`) |
| Runs terminal commands | Yes | No — tells you what to run |
| Edits files | Yes | No — advises only |
| API key | Claude subscription | GitHub subscription |
| Model choice | Claude only | GPT-4o, Claude Sonnet, Gemini, and others |

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

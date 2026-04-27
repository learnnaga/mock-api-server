# Mock API Server Generator

A self-contained toolkit for generating and running mock HTTP servers from OpenAPI specs. Comes with six pre-built mocks for enterprise APIs and an optional Kubernetes Helm chart generator.

## Repository structure

```
mock-api-server/
├── generate_mock_server.py        # Core generator — works standalone, no AI needed
├── mock_portal.py                 # Unified Swagger UI portal for all mocks
├── mock-data-config.yaml          # Response count / field override config
├── portal-config.json             # Registry of running mock servers
├── SKILL.md                       # Claude Code skill definition (AI workflow)
├── CLAUDECODE_USAGE_README.md     # Full Claude Code usage guide
├── VSCODE_USAGE.md                # VS Code usage guide (no Claude Code required)
│
├── cisco-meraki-dashboard-api/        # Pre-built mock — Meraki (port 9090)
├── microsoft-defender-for-endpoint-api/  # Pre-built mock — Defender (port 9091)
├── verkada-api/                       # Pre-built mock — Verkada (port 9092)
├── crestron-xio-cloud-api/            # Pre-built mock — Crestron (port 9093)
├── microsoft-entra-id-api/            # Pre-built mock — Entra ID (port 9094)
└── microsoft-intune-api/              # Pre-built mock — Intune (port 9095)
```

## Quick start (no AI required)

```bash
# Generate a mock server from any OpenAPI spec
python generate_mock_server.py path/to/openapi.json --port 9090

# Start the generated mock
cd <api-name>/
pip install -r requirements.txt
python mock_server.py
```

See [VSCODE_USAGE.md](VSCODE_USAGE.md) for the complete standalone and VS Code workflow.

## Pre-built mocks

Six mock servers are included and ready to start immediately:

| Mock | Port | Key endpoints |
|------|------|--------------|
| Cisco Meraki Dashboard API | 9090 | Organizations, networks, devices, clients |
| Microsoft Defender for Endpoint | 9091 | Machines, alerts, software, vulnerabilities, logon users |
| Verkada | 9092 | Cameras, access control, alarms, sites |
| Crestron XiO Cloud | 9093 | Devices with IP/MAC, group control |
| Microsoft Entra ID | 9094 | Users, devices, groups, memberships |
| Microsoft Intune | 9095 | Managed devices, compliance policies, device users |

**Start a mock:**
```bash
cd cisco-meraki-dashboard-api
pip install -r requirements.txt
python mock_server.py
```

**Start the unified portal (Swagger UI for all mocks):**
```bash
pip install flask requests
python mock_portal.py
# Open http://localhost:8888
```

## AI-assisted usage

### Claude Code (CLI)

If you have [Claude Code](https://claude.ai/code) installed, open this folder and use natural-language prompts — the `SKILL.md` file teaches Claude the full workflow:

> "Generate a mock from `cisco-meraki-dashboard-api/openapi.json` on port 9090 with a Helm chart for ingress path `/meraki`"

> "Run smoke tests against the Defender mock on port 9091"

See [CLAUDECODE_USAGE_README.md](CLAUDECODE_USAGE_README.md) for the full guide.

### VS Code without Claude Code

Three options — standalone terminal, Cline extension, or Claude.ai web. See [VSCODE_USAGE.md](VSCODE_USAGE.md).

## Kubernetes deployment

Generate a `Dockerfile` and Helm chart alongside any mock:

```bash
# New mock with K8s artifacts
python generate_mock_server.py openapi.json --port 9090 --k8s --ingress-path /myapi

# Add K8s artifacts to an existing mock (leaves mock_server.py untouched)
python generate_mock_server.py openapi.json --port 9090 --k8s-only --ingress-path /myapi
```

All mocks use port `9090` inside Kubernetes — the ingress path differentiates them:
```
http://mock.cluster/meraki/*   → cisco-meraki-dashboard-api pod
http://mock.cluster/defender/* → microsoft-defender-for-endpoint-api pod
http://mock.cluster/entra/*    → microsoft-entra-id-api pod
```

## Requirements

- Python 3.9+
- `pip install flask pyyaml` (generator and portal)
- Docker + Helm (optional, for Kubernetes)
- Claude Code (optional, for AI-assisted workflow)

## Contributing

- **Add a new mock:** `python generate_mock_server.py <spec> --port <port>` — auto-registered in `portal-config.json`
- **Customise a mock:** edit `<api-name>/mock_server.py` — `MOCK_RESPONSES` dict and Flask routes are plain Python
- **Override at runtime:** `POST /mock-control` with `{"route": "GET /path", "body": {...}}`
- **Update data config:** edit `mock-data-config.yaml` and restart the mock

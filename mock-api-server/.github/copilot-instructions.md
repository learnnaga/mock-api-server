# Mock API Server — Copilot Instructions

This repo contains a Python-based mock API server generator and six pre-built mock servers for enterprise APIs. When answering questions about this project, always give the user the **exact terminal command** to run rather than general guidance.

## What this project does

`generate_mock_server.py` reads an OpenAPI 2.x or 3.x spec and produces a self-contained folder with:
- `mock_server.py` — a Flask HTTP server with one route per endpoint
- `requirements.txt` — pinned dependencies (`flask`, `pyyaml`)
- `QUICKSTART.md` — curl examples with auth pre-filled
- `Dockerfile` + `helm/<chart>/` — Kubernetes artifacts (only when `--k8s` or `--k8s-only` is passed)

## Generator flags

```
python generate_mock_server.py <spec_file> [options]

--port <n>              Port Flask listens on (use 9090 for K8s, any free port locally)
--endpoints <list>      Space-separated METHOD:/path pairs to mock (default: all)
--out-dir <dir>         Parent directory for the generated folder (default: spec directory)
--k8s                   Also generate Dockerfile + Helm chart
--k8s-only              Generate ONLY Dockerfile + Helm chart — leaves mock_server.py untouched
--ingress-path <path>   Ingress prefix, e.g. /meraki (default: /<api-slug>)
--ingress-class <name>  Ingress class (default: nginx)
--data-config <file>    Path to mock-data-config.yaml (auto-detected if omitted)
--run                   Start the server immediately after generating
--smoke-test            Generate → start → probe all routes → exit with 0/1
```

## Port conventions

- **Local development:** each mock uses a different port (9090 Meraki, 9091 Defender, 9092 Verkada, 9093 Crestron, 9094 Entra ID, 9095 Intune)
- **Kubernetes:** all mocks use port 9090 — the ingress path differentiates them

## Pre-built mocks

All six are ready to start without regenerating:

| Folder | Port | Ingress path |
|--------|------|-------------|
| `cisco-meraki-dashboard-api/` | 9090 | `/meraki` |
| `microsoft-defender-for-endpoint-api/` | 9091 | `/defender` |
| `verkada-api/` | 9092 | `/verkada` |
| `crestron-xio-cloud-api/` | 9093 | `/crestron` |
| `microsoft-entra-id-api/` | 9094 | `/entra` |
| `microsoft-intune-api/` | 9095 | `/intune` |

Start any mock: `cd <folder> && pip install -r requirements.txt && python mock_server.py`

## Key behaviours

- `AUTH_ENFORCE = False` by default — requests pass without credentials; set to `True` to enforce
- `GET /mock-auth-status` — always returns current auth config (never requires auth)
- `POST /mock-control` — override any response at runtime without restarting
- OAuth2 mocks include a token endpoint at the real IdP path — POST `client_id` + `client_secret` to get a mock JWT, then use it as `Authorization: Bearer <token>`

## Adding K8s artifacts to an existing mock

When `mock_server.py` was hand-edited and must not be overwritten, use `--k8s-only`:
```bash
python generate_mock_server.py microsoft-defender-for-endpoint-api/openapi.json \
    --port 9090 --k8s-only --ingress-path /defender --out-dir .
```

## mock-data-config.yaml

Controls how many items each endpoint returns and lets you override field values. Organised by API slug and endpoint path. Auto-discovered from the repo root.

```yaml
cisco-meraki-dashboard-api:
  endpoints:
    /api/v1/organizations:
      count: 3
      fields:
        name: "Acme Corp {index}"
```

## Portal

`python mock_portal.py` starts a Swagger UI portal at http://localhost:8888 with live status cards and Try It Out for all registered mocks.

---
name: mock-api-server
description: Generates a self-contained mock server folder (Flask server, requirements.txt, QUICKSTART.md) for selected endpoints from an OpenAPI 2.x/3.x spec, with auth middleware, auto-start, smoke-test client queries, optional Helm chart + Dockerfile for Kubernetes deployment, and a unified Swagger UI portal for all mocks
---

# Mock API Server from OpenAPI Spec

This skill reads an OpenAPI (Swagger 2.x or OpenAPI 3.x) spec — provided as a file path or pasted inline — and produces a **self-contained output folder** per spec containing everything needed to run, query, and debug a local HTTP mock server immediately.

Each spec gets its own isolated folder named after the API title (e.g. `cisco-meraki-dashboard-api/`), so multiple mock servers can live side-by-side without conflicts.

## Capabilities

- **Isolated output folder per spec**: Files are placed in a folder derived from the API title, keeping mocks for different APIs separate.
- **Spec parsing**: Accepts `.json`, `.yaml`, or `.yml` OpenAPI/Swagger specs from a local file path or inline content pasted into the conversation.
- **Selective endpoint mocking**: Mock all endpoints, or pick only the ones you need (e.g. `GET:/users`, `POST:/orders/{id}`).
- **Schema-driven response generation**: Walks `$ref`, `allOf`, `anyOf`, `oneOf`, `properties`, and `items` to synthesize realistic JSON bodies matching the declared response schema.
- **Format-aware values**: Generates plausible values for `date-time`, `date`, `email`, `uuid`, `uri` formats; integers, floats, booleans, enums, and nested objects/arrays.
- **Full real auth flow simulation**: For `oauth2` and `openIdConnect` schemes the generator always emits a **mock token endpoint** at the same path as the real identity provider (host stripped). Clients POST `client_id` + `client_secret` + `grant_type` exactly as they would against Azure AD / Okta / etc., receive a mock JWT, and use it in `Authorization: Bearer` headers for all API calls. No code changes are needed in the client — only the base URL changes.
- **Auth middleware for all scheme types**: Reads `securityDefinitions` / `components/securitySchemes` and emits `AUTH_ENFORCE` toggle, `AUTH_SCHEMES` config, and a `@before_request` gate. Supports `apiKey` (header/query/cookie), `http` bearer, `http` basic, `oauth2`, and `openIdConnect`. Token endpoint paths are always exempt from the auth gate.
- **`GET /mock-auth-status`**: Introspection endpoint — returns current `AUTH_ENFORCE` flag and all schemes with their `mock_value`s. Always open (not gated by auth).
- **Auto-start + smoke-test**: `--smoke-test` flag generates the folder, installs flask if needed, starts the server as a subprocess, probes every mocked endpoint, prints PASS/FAIL per route, kills the server, and exits with code 0/1.
- **`requirements.txt`**: Pinned `flask>=3.0` (plus `pyyaml>=6.0` for YAML specs).
- **`QUICKSTART.md`**: Auto-generated setup guide with install steps, start command, auth table, ready-to-run `curl` examples (with auth headers pre-filled), runtime override recipe, and a debug checklist.
- **Runtime override endpoint**: `POST /mock-control` swaps any response without restarting.
- **Base path support**: Respects OpenAPI 3 `servers[].url` path prefix and Swagger 2 `basePath`.
- **Kubernetes deployment (opt-in)**: `--k8s` flag additionally generates a `Dockerfile` and a full Helm chart under `helm/<chart-name>/`. Each mock gets its own ingress path prefix (default: `/<api-slug>`) that is **rewritten** by the nginx ingress controller before the request reaches Flask — so the Flask server always receives the original API paths unchanged. Multiple mocks can share a single cluster ingress on different path prefixes.
- **Unified Swagger UI portal**: `mock_portal.py` (port 8888) provides a single homepage with live status cards for every registered mock, plus full Swagger UI per mock with auth credentials pre-filled and all "Try It Out" requests proxied through the portal to the live mock server. Each generated mock is **automatically registered** in `portal-config.json`. Supports API key, Bearer, and OAuth2 two-step flows (tokenUrl rewritten through the proxy).

## Input Requirements

Provide **one** of the following:

1. **File path** to an OpenAPI spec: `./petstore.yaml`, `/tmp/api-spec.json`, etc.
2. **Pasted spec content** directly in the chat — the skill will write it to a temp file first.

Optional parameters:

| Parameter | Default | Example |
|-----------|---------|---------|
| Endpoints to mock | all endpoints | `GET:/pets`, `POST:/pets`, `DELETE:/pets/{id}` |
| HTTP port | `8080` | `port 3000` |
| Output parent directory | spec file directory | `--out-dir ~/mocks` |
| Run immediately | false | "start the server after generating" |
| Smoke test | false | "generate and run test queries" |
| Generate K8s artifacts | false | `--k8s` or "also generate helm chart" |
| Ingress path prefix | `/<api-slug>` | `--ingress-path /meraki` |
| Ingress class | `nginx` | `--ingress-class traefik` |
| Data config file | auto-detected | `--data-config mock-data-config.yaml` |

## Output — folder structure

For a spec with `info.title: Cisco Meraki Dashboard API`:

**Without `--k8s`** (default):
```
cisco-meraki-dashboard-api/
├── mock_server.py    # Flask server — routes, auth middleware, /mock-control, /mock-auth-status
├── requirements.txt  # flask>=3.0 (+ pyyaml if spec is YAML)
└── QUICKSTART.md     # install → start → auth table → curl examples → debug checklist
```

**With `--k8s`**:
```
cisco-meraki-dashboard-api/
├── mock_server.py
├── requirements.txt
├── QUICKSTART.md
├── Dockerfile        # python:3.11-slim image, exposes server port
└── helm/
    └── cisco-meraki-dashboard-api/
        ├── Chart.yaml
        ├── values.yaml          # replicaCount, image, service, ingress settings
        └── templates/
            ├── _helpers.tpl
            ├── deployment.yaml  # liveness + readiness probes on /mock-auth-status
            ├── service.yaml     # ClusterIP on server port
            └── ingress.yaml     # path-rewriting nginx ingress
```

### `mock_server.py` sections

| Section | Description |
|---------|-------------|
| `MOCK_RESPONSES` dict | Override any response at startup by editing this dict |
| `AUTH_ENFORCE` flag | `False` = bypass (log only), `True` = enforce credentials |
| `AUTH_SCHEMES` dict | One entry per security scheme with `mock_value` for testing |
| `_validate_scheme()` | Checks apiKey header/query/cookie, bearer, basic, oauth2 |
| `check_auth()` | `@before_request` gate — skips `/mock-control` and `/mock-auth-status` |
| `GET /mock-auth-status` | Returns current auth config as JSON |
| Route functions | One per mocked endpoint; body stored as `json.loads("""...""")` |
| `POST /mock-control` | Runtime response override |

## Authentication

### OAuth2 / openIdConnect — real two-step flow (always generated)

When the spec declares an `oauth2` or `openIdConnect` scheme the generator **always** emits a mock token endpoint that mirrors the real identity provider path. This means client code written against the real API works against the mock with only a base-URL change.

```
Step 1 — Token acquisition (same path as real IdP, any credentials accepted)
  POST http://localhost:<port>/<tenant-id>/oauth2/v2.0/token
  Body: client_id=<app-id> & client_secret=<secret>
        & grant_type=client_credentials & scope=<scope>
  ← {"access_token": "<mock-jwt>", "token_type": "Bearer", "expires_in": 3599}

Step 2 — API call (token from Step 1)
  GET http://localhost:<port>/api/machines
  Authorization: Bearer <mock-jwt>
```

The `access_token` returned by the mock token endpoint is pre-wired to satisfy `AUTH_SCHEMES` validation, so Step 1 → Step 2 works end-to-end without any manual token copying.

QUICKSTART.md always shows the two-step curl flow with `$TOKEN` shell variable for OAuth2 APIs.

### All supported scheme types

| Scheme type | Mock token endpoint generated? | How Step 2 is validated |
|---|---|---|
| `oauth2` | **Yes** — at the spec's `tokenUrl` path (host stripped) | `Authorization: Bearer <access_token from Step 1>` |
| `openIdConnect` | **Yes** — at `/oauth2/token` | `Authorization: Bearer <token>` |
| `http` bearer | No — token provided directly | `Authorization: Bearer <mock_value>` |
| `http` basic | No | Base64 `user:password` in `Authorization` |
| `apiKey` header | No | Exact header value match |
| `apiKey` query | No | Exact query param match |
| `apiKey` cookie | No | Exact cookie match |

### Bypass vs enforce mode

| `AUTH_ENFORCE` | Behaviour |
|---|---|
| `False` (default) | All requests pass; credentials logged but not checked |
| `True` | Token/key required; wrong or missing → `401` with hint |

Token endpoints and `/mock-control` / `/mock-auth-status` are always exempt from the gate.

```python
# In mock_server.py — switch to enforce mode
AUTH_ENFORCE = True
```

Introspect at runtime:
```bash
curl -s http://localhost:<port>/mock-auth-status | python3 -m json.tool
```

## How to Use

**Mock all endpoints from a local spec:**
> "Generate a mock server from `./openapi.yaml`"

**Mock specific endpoints on a custom port:**
> "Create a mock for `GET:/users` and `POST:/users` from `petstore.json` on port 9090"

**Generate, start, and run smoke-test queries immediately:**
> "Generate a mock server from `meraki.json` and run test queries"

**Specify output location:**
> "Generate mocks from `api-spec.yaml` into `~/projects/mocks`"

**Paste spec inline:**
> "Here is my OpenAPI spec: [paste]. Mock `GET:/products` and `GET:/products/{id}` and start it."

**Generate with Kubernetes Helm chart:**
> "Generate a mock from `meraki.json` with a Helm chart, ingress path `/meraki`"

**Generate multiple mocks for cluster deployment:**
> "Generate mocks for `meraki.json` on port 9090 and `defender.json` on port 9091, both with Helm charts — use `/meraki` and `/defender` as ingress paths"

## Kubernetes Deployment

### Enabling K8s artifact generation

Add `--k8s` to any generator invocation:

```bash
python generate_mock_server.py <spec_file> \
    --endpoints <METHOD:/path ...> \
    --port <port> \
    --k8s \
    [--ingress-path /my-prefix] \
    [--ingress-class nginx]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--k8s` | off | Generate `Dockerfile` + `helm/<chart>/` alongside the Flask server |
| `--k8s-only` | off | Generate **only** `Dockerfile` + `helm/<chart>/` — leaves `mock_server.py` untouched. Use when the server already exists and was hand-edited. |
| `--ingress-path` | `/<api-slug>` | Ingress path prefix for this mock (e.g. `/meraki`, `/defender`) |
| `--ingress-class` | `nginx` | Kubernetes ingress class (`nginx`, `traefik`, `haproxy`, etc.) |

### Port for K8s deployments

Since each mock runs in its own pod, all K8s mocks can use the **same internal port** (`9090`). The ingress path (`/meraki`, `/defender`, etc.) differentiates them — port is irrelevant to external callers. Always pass `--port 9090` for K8s artifact generation:

```bash
python generate_mock_server.py meraki.json   --port 9090 --k8s --ingress-path /meraki
python generate_mock_server.py defender.json --port 9090 --k8s --ingress-path /defender
python generate_mock_server.py intune.json   --port 9090 --k8s --ingress-path /intune
```

Local development still uses distinct ports to avoid conflicts (9090, 9091, 9092…). Only the K8s artifacts (Dockerfile `EXPOSE`, Helm chart service port, liveness probe) need to match `--port`.

### Choosing the ingress path (API name in URL)

The default `--ingress-path` is derived from the API title slug, which is often long (e.g. `/microsoft-defender-for-endpoint-api`). Always override it with a short, stable path that becomes the **external URL segment identifying the API**:

| Mock | Default slug (too long) | Recommended `--ingress-path` | External URL |
|------|------------------------|------------------------------|--------------|
| Cisco Meraki Dashboard API | `/cisco-meraki-dashboard-api` | `/meraki` | `http://mock.example.com/meraki/api/v1/organizations` |
| Microsoft Defender for Endpoint | `/microsoft-defender-for-endpoint-api` | `/defender` | `http://mock.example.com/defender/api/machines` |
| Microsoft Entra ID API | `/microsoft-entra-id-api` | `/entra` | `http://mock.example.com/entra/v1.0/users` |
| Microsoft Intune API | `/microsoft-intune-api` | `/intune` | `http://mock.example.com/intune/v1.0/deviceManagement/managedDevices` |
| Verkada API | `/verkada-api` | `/verkada` | `http://mock.example.com/verkada/cameras/v1/devices` |
| Crestron XiO Cloud API | `/crestron-xio-cloud-api` | `/crestron` | `http://mock.example.com/crestron/api/v1/device/accountid/acc-1/devices` |

### How path rewriting works

The generated ingress uses the nginx `rewrite-target` annotation to strip the prefix before the request reaches Flask:

```
Client request:   GET http://mock.local/meraki/api/v1/organizations
Ingress rule:     path = /meraki(/|$)(.*)   →   rewrite-target = /$2
Flask receives:   GET /api/v1/organizations
```

This means Flask routes (`/api/v1/organizations`) work identically whether the server is accessed locally (direct port) or through the cluster ingress (via path prefix). No changes to `mock_server.py` are needed.

The same rewrite works for control endpoints:
```
GET  http://mock.local/meraki/mock-auth-status  →  Flask: GET /mock-auth-status
POST http://mock.local/meraki/mock-control       →  Flask: POST /mock-control
```

### Running multiple mocks on a single cluster ingress

Deploy each mock on a different ingress path prefix. All share the same ingress hostname:

```
http://mock.local/meraki/*    →  cisco-meraki-dashboard-api service : 9090
http://mock.local/defender/*  →  microsoft-defender-for-endpoint-api service : 9091
http://mock.local/petstore/*  →  swagger-petstore service : 9092
```

Generate each with its own `--ingress-path`:

```bash
python generate_mock_server.py meraki.json   --port 9090 --k8s --ingress-path /meraki
python generate_mock_server.py defender.json --port 9091 --k8s --ingress-path /defender
python generate_mock_server.py petstore.yaml --port 9092 --k8s --ingress-path /petstore
```

### Deploy a mock to Kubernetes

```bash
# 1. Build and push the container image
cd cisco-meraki-dashboard-api
docker build -t cisco-meraki-dashboard-api:latest .
docker tag  cisco-meraki-dashboard-api:latest <registry>/cisco-meraki-dashboard-api:latest
docker push <registry>/cisco-meraki-dashboard-api:latest

# 2. Update image in values.yaml (or pass inline)
#    image.repository: <registry>/cisco-meraki-dashboard-api

# 3. Install the Helm chart
helm install meraki-mock ./helm/cisco-meraki-dashboard-api \
  --set image.repository=<registry>/cisco-meraki-dashboard-api \
  --set ingress.host=mock.local

# 4. Verify
kubectl get pods,svc,ingress
curl http://mock.local/meraki/mock-auth-status
```

### Upgrade / re-deploy after regeneration

```bash
# Regenerate (port, endpoints, or spec changed)
python generate_mock_server.py meraki.json --port 9090 --k8s --ingress-path /meraki

# Rebuild image and upgrade release
docker build -t <registry>/cisco-meraki-dashboard-api:latest .
docker push <registry>/cisco-meraki-dashboard-api:latest
helm upgrade meraki-mock ./helm/cisco-meraki-dashboard-api
```

### Dockerfile — build details and best practices

The generated `Dockerfile` uses a minimal `python:3.11-slim` base and follows these conventions:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mock_server.py .
EXPOSE <port>
CMD ["python", "mock_server.py"]
```

Key points:
- **`requirements.txt` is copied first** — lets Docker cache the pip layer; rebuilds skip pip install when only `mock_server.py` changes.
- **`--no-cache-dir`** — keeps the image lean (no pip download cache saved inside the layer).
- **`EXPOSE <port>`** — documents the port; does not publish it. The Helm chart's `service.yaml` and `values.yaml` use the same port.
- The image tag should match `values.yaml → image.tag`. Use a version tag (e.g. `v1.0.0`) in production rather than `latest` to control rollouts.

**Local build and test before pushing:**
```bash
cd microsoft-defender-for-endpoint-api

# Build
docker build -t defender-mock:local .

# Run locally (maps container port to host)
docker run --rm -p 9091:9091 defender-mock:local

# Verify
curl http://localhost:9091/mock-auth-status
```

**Build and push to a registry:**
```bash
# Docker Hub
docker build -t <dockerhub-user>/defender-mock:v1.0.0 .
docker push <dockerhub-user>/defender-mock:v1.0.0

# AWS ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker build -t <account>.dkr.ecr.<region>.amazonaws.com/defender-mock:v1.0.0 .
docker push <account>.dkr.ecr.<region>.amazonaws.com/defender-mock:v1.0.0

# GCP Artifact Registry
gcloud auth configure-docker <region>-docker.pkg.dev
docker build -t <region>-docker.pkg.dev/<project>/mocks/defender-mock:v1.0.0 .
docker push <region>-docker.pkg.dev/<project>/mocks/defender-mock:v1.0.0
```

### External access — LoadBalancer IP and DNS

After `helm install`, the nginx ingress controller assigns an external IP via a LoadBalancer Service. Discover it with:

```bash
# Wait for EXTERNAL-IP to be assigned (may take ~60s on cloud providers)
kubectl get svc -n ingress-nginx ingress-nginx-controller --watch

# Once assigned, grab it
INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Ingress IP: $INGRESS_IP"
```

**Cloud DNS (production):** Create an A record pointing `mock.yourdomain.com` → `$INGRESS_IP`.

**Local `/etc/hosts` (dev/testing):** Map the hostname without DNS:
```bash
# Add entry (run once; requires sudo)
echo "$INGRESS_IP  mock.local" | sudo tee -a /etc/hosts

# Verify
curl http://mock.local/defender/mock-auth-status
```

For **minikube** or **kind** (local clusters), the LoadBalancer IP stays `<pending>`. Use `minikube tunnel` or port-forward instead:
```bash
# minikube
minikube tunnel          # assigns a real local IP to LoadBalancer services
# OR port-forward directly to the pod
kubectl port-forward deployment/microsoft-defender-for-endpoint-api 9091:9091

curl http://localhost:9091/api/machines
```

### Ingress redirect verification

After deploying, confirm the nginx rewrite is working correctly with these steps:

**1. Check the ingress rule was created:**
```bash
kubectl get ingress
kubectl describe ingress microsoft-defender-for-endpoint-api
# Look for: "rewrite-target: /$2" annotation and the path rule "/defender(/|$)(.*)"
```

**2. Confirm path rewrite reaches Flask:**
```bash
# With rewrite working — Flask receives /mock-auth-status, returns JSON
curl -v http://mock.local/defender/mock-auth-status

# Expected: HTTP 200 with {"auth_enforce": false, "schemes": {...}}
# If you get 404: the rewrite annotation is missing or nginx config hasn't reloaded
```

**3. Test a real API endpoint through the ingress:**
```bash
# Unauthenticated (AUTH_ENFORCE=False by default)
curl http://mock.local/defender/api/machines

# With token (get one first via the mock token endpoint)
TOKEN=$(curl -s -X POST http://mock.local/defender/<tenant-id>/oauth2/v2.0/token \
  -d "client_id=test&client_secret=test&grant_type=client_credentials" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -H "Authorization: Bearer $TOKEN" http://mock.local/defender/api/machines
```

**4. Confirm path variable routes work:**
```bash
# Path param should be forwarded correctly after prefix strip
curl http://mock.local/defender/api/machines/machine-001
```

### Troubleshooting ingress issues

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `404` on `/defender/api/machines` but `200` on `localhost:9091/api/machines` | Rewrite annotation not applied | Confirm `nginx.ingress.kubernetes.io/rewrite-target: /$2` is in the ingress YAML; `kubectl describe ingress` shows annotations |
| `404` on `/defender` (no trailing slash) but `200` on `/defender/` | Path regex missing `|$` alternative | Ingress path must be `/defender(/|$)(.*)`, not `/defender/(.*)` |
| `308 Permanent Redirect` loop or redirect to `/defender/` | Nginx redirect for missing trailing slash | Add annotation `nginx.ingress.kubernetes.io/use-regex: "true"` alongside `rewrite-target` |
| `503 Service Unavailable` | Pod not ready or service port mismatch | `kubectl get pods` — check STATUS; `kubectl logs <pod>` — check Flask startup; confirm `service.yaml` port matches `values.yaml` `service.port` |
| `Connection refused` from outside cluster | LoadBalancer `EXTERNAL-IP` still `<pending>` | Run `minikube tunnel` or use port-forward; check cloud provider quotas |
| Token endpoint returns `404` via ingress | Token path not registered as a Flask route or rewrite drops tenant segment | Confirm the token endpoint path (e.g. `/abc123/oauth2/v2.0/token`) is registered in `mock_server.py`; check Flask logs |
| Ingress works but `/mock-control` POST returns `404` | Trailing slash or method mismatch | Use `POST http://mock.local/defender/mock-control` (no trailing slash); Flask route is `POST /mock-control` |

### What each Helm template does

| Template | Contents |
|----------|----------|
| `deployment.yaml` | Single-replica Deployment; liveness + readiness probes on `GET /mock-auth-status` |
| `service.yaml` | ClusterIP Service on the server port |
| `ingress.yaml` | nginx Ingress with `rewrite-target` annotation; TLS optional via `values.yaml` |
| `_helpers.tpl` | Standard name/label helpers |

### values.yaml key settings

```yaml
ingress:
  enabled: true
  className: "nginx"
  path: "/meraki"       # change per mock
  host: "mock.local"    # shared across all mocks
  tls: []               # add TLS secret here if needed
```

### Claude prompts for K8s generation

> Generate a mock from `meraki.json` on port 9090 and also produce a Helm chart with ingress path `/meraki`

> Generate mocks for both Meraki and Defender on port 9090 with K8s artifacts — use `/meraki` and `/defender` as ingress paths

> Regenerate the Meraki mock on port 9090 with `--k8s` using a Traefik ingress class

> Show me how to deploy the generated Helm chart to my cluster

**The mock server already exists and was hand-edited — only add the Helm chart:**

> The `microsoft-defender-for-endpoint-api/` mock already exists and was customized. Add a Helm chart and Dockerfile for it on port 9090 with ingress path `/defender` — do not touch `mock_server.py`.

This maps to:
```bash
python generate_mock_server.py microsoft-defender-for-endpoint-api/openapi.json \
    --port 9090 \
    --k8s-only \
    --ingress-path /defender \
    --out-dir .
```

`--k8s-only` generates only `Dockerfile` and `helm/microsoft-defender-for-endpoint-api/` — `mock_server.py`, `requirements.txt`, `QUICKSTART.md`, and `openapi.json` are left completely untouched.

## Data Configuration — mock-data-config.yaml

`mock-data-config.yaml` controls how many items each endpoint returns and lets you override specific field values. It is organised by API slug (folder name) and endpoint path, exactly as they appear in the OpenAPI spec.

```yaml
# One section per API slug (= slugified info.title)
cisco-meraki-dashboard-api:
  endpoints:

    /api/v1/organizations:
      count: 3                    # generate 3 items in the array
      fields:
        name: "Acme Corp {index}" # {index} → 0-based item number
        licensing:
          model: co-term          # nested field override

    /api/v1/organizations/{organizationId}/networks:
      count: 4
      fields:
        name: "Office Network {index}"
        productTypes: [appliance, switch, wireless]

microsoft-defender-for-endpoint-api:
  endpoints:

    /api/machines:
      count: 5
      nested:
        array_key: value          # response wraps list: {"value": [...]}
        count_key: "@odata.count" # set this key to count too
      fields:
        osPlatform: Windows10
        healthStatus: Active

verkada-api:
  endpoints:

    /cameras/v1/devices:
      count: 6
      nested:
        array_key: cameras        # response: {"cameras": [...]}
      fields:
        status: online
        model: CD52
```

### Supported keys per endpoint

| Key | Type | Description |
|-----|------|-------------|
| `count` | integer | Number of top-level items to generate |
| `fields` | mapping | Field overrides applied to every item; `{index}` is replaced with the 0-based item number; nested dicts are deep-merged |
| `nested.array_key` | string | When the response wraps an array (e.g. `{"value": [...]}`) — the key that holds the list |
| `nested.count_key` | string | Key in the wrapper object to set to `count` (e.g. `"@odata.count"`) |

### Auto-discovery

The generator looks for `mock-data-config.yaml` in this order (first match wins):

1. Path passed via `--data-config`
2. Same directory as `generate_mock_server.py`
3. Same directory as the spec file
4. Current working directory

If no file is found, schema-derived defaults are used (no behaviour change).

## Scripts

- [generate_mock_server.py](generate_mock_server.py): Core generator — parses spec, resolves `$ref` chains, synthesizes mock values, generates auth middleware, creates output folder, writes all files. Also saves `openapi.json` and auto-updates `portal-config.json`. Flags: `--run`, `--smoke-test`, `--k8s`, `--ingress-path`, `--ingress-class`, `--data-config`.
- [mock-data-config.yaml](mock-data-config.yaml): YAML config controlling response item counts and field overrides per endpoint. Auto-discovered from the generator directory; supports all three current mocks out of the box.
- [mock_portal.py](mock_portal.py): Unified Swagger UI portal (port 8888). Homepage with live status cards, Swagger UI per mock with auto-filled auth, transparent proxy, spec rewriter. Reads `portal-config.json` — restart to pick up new mocks. Dependencies: `flask`, `requests`.
- [portal-config.json](portal-config.json): Registry of all mock servers. Auto-updated by the generator. Edit manually to add, remove, or change `auth_enforce` / `port` for a mock.

## Step-by-Step Workflow Claude Follows

### A. Initial generation

When this skill is first invoked for a spec, Claude will:

1. **Locate or receive the spec** — confirm the file path exists, or write pasted content to `/tmp/openapi_spec.json`.
2. **Ask for endpoint selection** if not specified — list available paths and ask which to mock (or confirm "all").
3. **Ask for port** if not specified (default 8080).
4. **Run the generator:**
   ```bash
   python generate_mock_server.py <spec_file> \
       --endpoints <METHOD:/path ...> \
       --port <port> \
       [--out-dir <parent_dir>] \
       [--k8s --ingress-path /<prefix> --ingress-class nginx]
   ```
5. **Report the generated folder** — list `mock_server.py`, `requirements.txt`, `QUICKSTART.md` (and `Dockerfile`, `helm/<chart>/` if `--k8s`), and note any detected auth schemes.
6. **Install dependencies:**
   ```bash
   pip install -r <out_dir>/requirements.txt
   ```
7. **Start the server** (background subprocess):
   ```bash
   python <out_dir>/mock_server.py &
   ```
8. **Run client queries** — execute each `curl` from `QUICKSTART.md` section 4, capturing HTTP status and response body.
9. **Report results** — print PASS (2xx) / FAIL (non-2xx or error) per endpoint, show response bodies.
10. **Debug any failures** using the checklist below.
11. **Keep server running** unless the user asks to stop it, or offer to run `--smoke-test` for a self-contained generate+test+exit cycle.

> **Shortcut**: use `--smoke-test` to collapse steps 4–9 into one command.

---

### B. Updating an existing mock — keeping QUICKSTART.md in sync

`QUICKSTART.md` reflects the state of `mock_server.py` at generation time. When the mock changes, QUICKSTART.md must be updated to stay accurate. Claude must detect which type of change occurred and apply the correct update strategy.

#### Trigger → update strategy

| What changed | Strategy | Command |
|---|---|---|
| Endpoints added or removed | **Full regeneration** — re-run the generator with the new endpoint list | `python generate_mock_server.py <spec> --endpoints ... --port <port> --out-dir <dir>` |
| Port changed | **Full regeneration** — every URL in QUICKSTART.md embeds the port | Same as above with new `--port` |
| Spec file updated (new schemas, new auth schemes) | **Full regeneration** | Same as above |
| `mock_value` edited in `mock_server.py` | **Targeted QUICKSTART.md edit** — update the auth table row and the curl flag for that scheme | Edit `QUICKSTART.md` sections 4 and "Authentication" |
| `AUTH_ENFORCE` toggled | **Targeted QUICKSTART.md edit** — update the auth table note about bypass/enforce mode | Edit the auth section preamble |
| Static response body changed directly in `mock_server.py` | **No QUICKSTART.md update needed** — curl examples don't embed response bodies | No change required |
| `/mock-control` override applied at runtime | **No QUICKSTART.md update needed** — runtime state, not persisted | No change required |

#### Full regeneration (safe default)

When in doubt, re-run the generator. It **overwrites** all three files (`mock_server.py`, `requirements.txt`, `QUICKSTART.md`) from the spec. Any manual edits to `mock_server.py` (custom `mock_value`s, hand-tuned bodies) will be **lost** — warn the user before doing this.

```bash
# Stop the running server first
lsof -ti :<port> | xargs kill -9

# Regenerate
python generate_mock_server.py <spec_file> \
    --endpoints <METHOD:/path ...> \
    --port <port> \
    --out-dir <parent_dir>

# Restart
python <out_dir>/mock_server.py &
```

#### Targeted QUICKSTART.md edit (when mock_server.py was hand-edited)

When the user has manually edited `mock_server.py` (e.g. changed a `mock_value` or set `AUTH_ENFORCE = True`) and does **not** want to lose those edits:

1. Read the current `mock_server.py` to extract the live values.
2. Edit only the affected lines in `QUICKSTART.md` using the Edit tool — do not regenerate.
3. Re-run any relevant `curl` queries to confirm the QUICKSTART examples still work.

**Specific fields to sync:**

- `AUTH_ENFORCE` value → update the sentence "The mock server runs in **bypass/enforce mode**" in the Authentication section.
- `mock_value` for a scheme → update the "Mock credential" column in the auth table AND the `-H`/`--user` flag in the corresponding curl example in section 4.
- Port number → update every URL in sections 2, 4, 5 — prefer full regeneration instead.

#### Detecting staleness

Before running queries, Claude should check whether QUICKSTART.md is stale:

```bash
# Extract port from mock_server.py
grep "app.run" <out_dir>/mock_server.py

# Extract AUTH_ENFORCE from mock_server.py
grep "AUTH_ENFORCE" <out_dir>/mock_server.py | head -1

# Extract route paths from mock_server.py
grep "@app.route" <out_dir>/mock_server.py
```

Compare these against the values embedded in `QUICKSTART.md`. If they differ, apply the appropriate update strategy above before running smoke-test queries.

## Debugging Failed Queries

When a query returns an unexpected result, work through this checklist in order:

| Symptom | Diagnosis steps | Fix |
|---------|----------------|-----|
| `Connection refused` | Server process not running | `python mock_server.py` in the output folder |
| `Address already in use` | Port taken by another process | `lsof -i :<port>` to identify it; use `--port <other>` |
| `401 Unauthorized` | `AUTH_ENFORCE=True` + wrong/missing credential | Check `GET /mock-auth-status` for expected value; send `mock_value` or set `AUTH_ENFORCE=False` |
| `404 Not Found` | Path mismatch — wrong base path or param format | Check `basePath`/`servers[].url`; all routes include the prefix |
| `500 Internal Server Error` | Syntax error in generated file | Run `python -c "import mock_server"` in the folder to surface the traceback |
| `ModuleNotFoundError: flask` | Deps not installed | `pip install -r requirements.txt` |
| Stale/unexpected response body | `MOCK_RESPONSES` override active | `POST /mock-control` with the key to reset, or restart server |
| Auth header not being sent | curl flag not in command | Check `GET /mock-auth-status` for scheme type and expected header name |

## QUICKSTART.md contents (auto-generated per spec)

- **Prerequisites** — Python 3.9+, pip
- **Install step** — `pip install -r requirements.txt`
- **Start command** with expected console output
- **Mocked endpoints** list with summaries
- **Authentication table** — scheme name, type, mock credential, ready-to-use curl flag
- **`curl` examples** — one per endpoint, auth headers pre-filled, bodies for POST/PUT/PATCH
- **Runtime override** recipe for `POST /mock-control`
- **Debug checklist** — common symptoms, causes, fixes

## Best Practices

1. **Inline examples win**: `example` fields in the spec are used verbatim — richer spec = richer mocks.
2. **One folder per spec**: Multiple specs produce separate folders, each independently startable on its own port.
3. **Bypass auth first**: Leave `AUTH_ENFORCE=False` while building your client; switch to `True` when testing auth flows.
4. **Use `/mock-auth-status`**: Before debugging a 401, confirm what credential the server expects.
5. **Use `/mock-control` for error paths**: Inject `4xx`/`5xx` without touching code or restarting.
6. **Run `--smoke-test` in CI**: The exit code is 0 (all pass) or 1 (any fail), suitable for pipeline gates.

## Limitations

- Generates static mock data — responses do not mutate based on request body (use `/mock-control` for dynamic scenarios).
- Auth validation in enforce mode checks for exact credential match against `mock_value`; it does not simulate token expiry or real OAuth flows.
- `oneOf`/`anyOf` always picks the first sub-schema variant.
- Recursive schemas are capped at depth 5 to prevent infinite loops.
- Only `application/json` response bodies are generated; multipart, binary, or XML responses return empty objects.
- Requires Python 3.9+ and `flask` (`pip install -r requirements.txt`); YAML specs also require `pyyaml` (auto-included).
- `--smoke-test` requires `curl` on PATH for HTTP method-specific probes; falls back to `urllib` for GET.
- `--k8s` generates Helm chart and Dockerfile but does **not** build or push the container image — that step is left to the user (`docker build` + `docker push`).
- The generated Helm chart targets **nginx ingress controller** by default. For Traefik or other controllers, set `--ingress-class` and manually adjust the rewrite annotation in `templates/ingress.yaml` if needed (Traefik uses middleware instead of annotations).
- `values.yaml` sets `image.pullPolicy: IfNotPresent` — update to `Always` when iterating on image changes in a cluster.

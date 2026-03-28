---
name: mock-api-server
description: Generates a self-contained mock server folder (Flask server, requirements.txt, QUICKSTART.md) for selected endpoints from an OpenAPI 2.x/3.x spec, with auth middleware, auto-start, and smoke-test client queries
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

## Output — folder structure

For a spec with `info.title: Cisco Meraki Dashboard API`:

```
cisco-meraki-dashboard-api/
├── mock_server.py    # Flask server — routes, auth middleware, /mock-control, /mock-auth-status
├── requirements.txt  # flask>=3.0 (+ pyyaml if spec is YAML)
└── QUICKSTART.md     # install → start → auth table → curl examples → debug checklist
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

## Scripts

- [generate_mock_server.py](generate_mock_server.py): Core generator — parses spec, resolves `$ref` chains, synthesizes mock values, generates auth middleware, creates output folder, writes all three files. Flags: `--run` (exec server), `--smoke-test` (start + probe + report + exit).

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
       [--out-dir <parent_dir>]
   ```
5. **Report the generated folder** — list `mock_server.py`, `requirements.txt`, `QUICKSTART.md`, and note any detected auth schemes.
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

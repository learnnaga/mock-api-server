#!/usr/bin/env python3
"""
OpenAPI Mock Server Generator

Parses an OpenAPI 2.x/3.x spec and generates a self-contained output folder with:
  - mock_server.py   Flask HTTP server (one route per endpoint, auth middleware)
  - requirements.txt pinned dependencies
  - QUICKSTART.md    install → start → auth-aware curl examples → debug guide

Usage:
    python generate_mock_server.py <spec_file> [--endpoints GET:/users POST:/users] [--port 8080]
    python generate_mock_server.py <spec_file> --run          # generate + start immediately
    python generate_mock_server.py <spec_file> --smoke-test   # generate + start + run queries + report
"""

import argparse
import json
import os
import re
import random
import string
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Spec loading
# ---------------------------------------------------------------------------

def load_spec(path: str) -> dict:
    """Load OpenAPI spec from JSON or YAML file."""
    try:
        import yaml
    except ImportError:
        yaml = None  # type: ignore[assignment]

    with open(path) as f:
        content = f.read()

    if path.endswith((".yaml", ".yml")):
        if yaml is None:
            print("ERROR: pyyaml is required for YAML specs.  pip install pyyaml")
            sys.exit(1)
        return yaml.safe_load(content)
    return json.loads(content)


# ---------------------------------------------------------------------------
# Schema traversal helpers
# ---------------------------------------------------------------------------

def resolve_ref(spec: dict, ref: str) -> dict:
    parts = ref.lstrip("#/").split("/")
    node = spec
    for part in parts:
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


def generate_example_value(schema: dict, spec: dict, depth: int = 0) -> Any:
    """Recursively generate a fake value matching the given JSON Schema."""
    if depth > 5:
        return None
    if "$ref" in schema:
        schema = resolve_ref(spec, schema["$ref"])
    if "example" in schema:
        return schema["example"]
    if "enum" in schema:
        return schema["enum"][0]

    schema_type = schema.get("type")

    if "allOf" in schema:
        result = {}
        for sub in schema["allOf"]:
            val = generate_example_value(sub, spec, depth + 1)
            if isinstance(val, dict):
                result.update(val)
        return result
    if "anyOf" in schema or "oneOf" in schema:
        options = schema.get("anyOf") or schema.get("oneOf")
        return generate_example_value(options[0], spec, depth + 1)
    if schema_type == "object" or "properties" in schema:
        props = schema.get("properties", {})
        return {k: generate_example_value(v, spec, depth + 1) for k, v in props.items()}
    if schema_type == "array":
        items = schema.get("items", {})
        return [generate_example_value(items, spec, depth + 1)]
    if schema_type == "string":
        fmt = schema.get("format", "")
        if fmt == "date-time":  return "2024-01-15T10:30:00Z"
        if fmt == "date":       return "2024-01-15"
        if fmt == "email":      return "user@example.com"
        if fmt == "uuid":       return "550e8400-e29b-41d4-a716-446655440000"
        if fmt == "uri":        return "https://example.com/resource"
        if fmt == "password":   return "***"
        if schema.get("pattern"):
            return f"<matches: {schema['pattern']}>"
        return "".join(random.choices(string.ascii_lowercase, k=max(schema.get("minLength", 5), 5)))
    if schema_type == "integer":
        return random.randint(int(schema.get("minimum", 1)), int(schema.get("maximum", 100)))
    if schema_type == "number":
        return round(random.uniform(0.0, 100.0), 2)
    if schema_type == "boolean":
        return True
    if schema_type == "null":
        return None
    return None


# ---------------------------------------------------------------------------
# Endpoint extraction
# ---------------------------------------------------------------------------

def extract_endpoints(spec: dict) -> List[dict]:
    endpoints = []
    for path, path_item in spec.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue
        for method in ("get", "post", "put", "patch", "delete", "options", "head"):
            op = path_item.get(method)
            if op:
                endpoints.append({"method": method.upper(), "path": path, "operation": op})
    return endpoints


def build_mock_response(operation: dict, spec: dict) -> Tuple[Any, int]:
    responses = operation.get("responses", {})
    for code in ("200", "201"):
        if code in responses:
            return _extract_response_body(responses[code], spec), int(code)
    for code, resp in responses.items():
        if str(code).startswith("2"):
            return _extract_response_body(resp, spec), int(code)
    if responses:
        first = next(iter(responses))
        return _extract_response_body(responses[first], spec), (int(first) if str(first).isdigit() else 200)
    return {}, 200


def _extract_response_body(response_obj: dict, spec: dict) -> Any:
    if "$ref" in response_obj:
        response_obj = resolve_ref(spec, response_obj["$ref"])
    for mime in ("application/json", "*/*"):
        if mime in response_obj.get("content", {}):
            return generate_example_value(response_obj["content"][mime].get("schema", {}), spec)
    schema = response_obj.get("schema")
    if schema:
        return generate_example_value(schema, spec)
    return {}


# ---------------------------------------------------------------------------
# Auth scheme extraction
# ---------------------------------------------------------------------------

def extract_auth_schemes(spec: dict) -> Dict[str, dict]:
    """
    Return a flat dict of {name: scheme_config} from the spec.
    Handles both Swagger 2 securityDefinitions and OpenAPI 3 components/securitySchemes.
    Each entry is augmented with a `mock_value` field for the generated server.
    """
    raw: Dict[str, dict] = {}

    # Swagger 2.x
    raw.update(spec.get("securityDefinitions", {}))
    # OpenAPI 3.x
    raw.update(spec.get("components", {}).get("securitySchemes", {}))

    schemes: Dict[str, dict] = {}
    for name, cfg in raw.items():
        import base64 as _b64
        scheme = dict(cfg)
        t = cfg.get("type", "")
        http_scheme = cfg.get("scheme", "").lower()

        if t == "apiKey":
            scheme["mock_value"] = f"mock-{name.lower().replace('_', '-')}-key"
        elif t == "http" and http_scheme == "bearer":
            scheme["mock_value"] = f"mock-bearer-{name.lower().replace('_', '-')}"
        elif t == "http" and http_scheme == "basic":
            scheme["mock_value"] = ["mock-user", "mock-password"]
        elif t in ("oauth2", "openIdConnect"):
            # Generate a realistic JWT-shaped token so clients that decode it don't crash
            hdr = _b64.urlsafe_b64encode(b'{"typ":"JWT","alg":"RS256"}').rstrip(b"=").decode()
            pay = _b64.urlsafe_b64encode(
                json.dumps({"sub": f"mock-{name}", "mock": True, "iss": "mock-idp"}).encode()
            ).rstrip(b"=").decode()
            scheme["mock_value"] = f"{hdr}.{pay}.mock-sig"
        else:
            scheme["mock_value"] = f"mock-{name.lower().replace('_', '-')}"

        schemes[name] = scheme
    return schemes


def extract_token_endpoints(schemes: Dict[str, dict]) -> List[dict]:
    """
    For each oauth2/openIdConnect scheme, extract the token endpoint URL path
    and return metadata needed to generate a Flask mock route for it.
    Returns list of dicts: {scheme_name, flow_type, flask_path, original_url,
                            grant_type, scopes, mock_value}
    """
    from urllib.parse import urlparse
    token_eps: List[dict] = []
    seen_paths: set = set()

    for name, cfg in schemes.items():
        t = cfg.get("type", "")

        if t == "oauth2":
            for flow_type, flow in cfg.get("flows", {}).items():
                token_url = flow.get("tokenUrl", "")
                if not token_url:
                    continue
                path = urlparse(token_url).path
                # Convert {param-name} → <param_name> (Flask variable rule, valid identifier)
                flask_path = re.sub(
                    r"\{([^}]+)\}",
                    lambda m: "<" + re.sub(r"[^a-zA-Z0-9_]", "_", m.group(1)) + ">",
                    path,
                )
                if flask_path in seen_paths:
                    continue
                seen_paths.add(flask_path)
                grant_type = {
                    "clientCredentials": "client_credentials",
                    "authorizationCode":  "authorization_code",
                    "implicit":           "implicit",
                    "password":           "password",
                }.get(flow_type, "client_credentials")
                token_eps.append({
                    "scheme_name":  name,
                    "flow_type":    flow_type,
                    "flask_path":   flask_path,
                    "original_url": token_url,
                    "grant_type":   grant_type,
                    "scopes":       flow.get("scopes", {}),
                    "mock_value":   cfg.get("mock_value", "mock-token"),
                })

        elif t == "openIdConnect":
            flask_path = "/oauth2/token"
            if flask_path not in seen_paths:
                seen_paths.add(flask_path)
                token_eps.append({
                    "scheme_name":  name,
                    "flow_type":    "openIdConnect",
                    "flask_path":   flask_path,
                    "original_url": cfg.get("openIdConnectUrl", ""),
                    "grant_type":   "client_credentials",
                    "scopes":       {},
                    "mock_value":   cfg.get("mock_value", "mock-token"),
                })

    return token_eps


def generate_token_endpoint_section(schemes: Dict[str, dict]) -> List[str]:
    """
    Return Flask route code that simulates the OAuth2 token-issuance step (Step 1).

    Each oauth2/openIdConnect scheme gets a POST endpoint at the same path as its
    real tokenUrl (host stripped). Any client_id / client_secret is accepted.
    The returned access_token matches AUTH_SCHEMES[name].mock_value so it works
    transparently in Step 2 (API calls with Authorization: Bearer <token>).
    """
    token_eps = extract_token_endpoints(schemes)
    if not token_eps:
        return []

    # Build MOCK_TOKEN_STORE entries
    store_entries: List[str] = []
    for te in token_eps:
        scope_str = " ".join(te["scopes"].keys()) if te["scopes"] else ""
        token_resp = {
            "access_token": te["mock_value"],
            "token_type":   "Bearer",
            "expires_in":   3599,
        }
        if scope_str:
            token_resp["scope"] = scope_str
        entry = json.dumps(token_resp, indent=8)
        entry_indented = "\n".join("    " + l for l in entry.splitlines())
        store_entries.append(f'    "{te["scheme_name"]}": {entry_indented},')

    lines = [
        "",
        "# ---------------------------------------------------------------------------",
        "# Mock token endpoint(s) — simulates Step 1 of the real OAuth2 auth flow",
        "#",
        "# Clients POST here with client_id + client_secret + grant_type (form-encoded",
        "# or JSON), exactly as they would against the real identity provider.",
        "# Any client_id / client_secret is accepted — this is a mock.",
        "#",
        "# The returned access_token matches AUTH_SCHEMES[*].mock_value so it works",
        "# transparently in Step 2 (API calls with Authorization: Bearer <token>).",
        "# ---------------------------------------------------------------------------",
        "",
        "MOCK_TOKEN_STORE: dict = {",
    ] + store_entries + ["}",  ""]

    seen_fn: set = set()
    for te in token_eps:
        fn_base = re.sub(r"[^a-zA-Z0-9_]", "_", te["flask_path"]).strip("_").lower()
        fn_name = f"{fn_base}_endpoint"
        if fn_name in seen_fn:
            continue
        seen_fn.add(fn_name)

        path_params = re.findall(r"<(\w+)>", te["flask_path"])
        fn_sig = ("def " + fn_name + "(" + ", ".join(path_params) + "):"
                  if path_params else f"def {fn_name}():")
        expected_grant = te["grant_type"]
        scheme_name    = te["scheme_name"]
        scope_str      = " ".join(te["scopes"].keys()) if te["scopes"] else ""

        lines += [
            f"# Token endpoint — scheme: {te['scheme_name']} ({te['flow_type']})",
            f"# Mirrors real URL: {te['original_url']}",
            f'@app.route("{te["flask_path"]}", methods=["POST"])',
            fn_sig,
            '    """Return a mock access token. Accepts any client_id / client_secret."""',
            "    data = request.get_json(force=True) if request.is_json else request.form.to_dict()",
            "    grant_type = data.get('grant_type', '')",
            f"    if grant_type != '{expected_grant}':",
            "        return jsonify({",
            "            'error': 'unsupported_grant_type',",
            f"            'error_description': f\"Expected grant_type='{expected_grant}', got: {{grant_type}}\"",
            "        }), 400",
            f"    token_data = dict(MOCK_TOKEN_STORE.get('{scheme_name}',",
            "                      next(iter(MOCK_TOKEN_STORE.values()))))",
            "    app.logger.debug('TOKEN  client_id=%s  grant_type=%s',",
            "                     data.get('client_id', '?'), grant_type)",
            "    return jsonify(token_data), 200",
            "",
        ]

    return lines


def auth_curl_flags(operation: dict, spec: dict, schemes: Dict[str, dict]) -> List[str]:
    """
    Return a list of -H / --user curl flags appropriate for the first security
    requirement of this operation (falls back to global security).
    Returns empty list if no security defined.
    """
    security_reqs = operation.get("security") or spec.get("security", [])
    if not security_reqs:
        return []

    # Pick the first non-empty requirement
    for req in security_reqs:
        if not req:          # {} means "no auth required" for this option
            return []
        scheme_name = next(iter(req))
        if scheme_name not in schemes:
            continue
        cfg = schemes[scheme_name]
        t = cfg.get("type", "")
        http_scheme = cfg.get("scheme", "").lower()
        mv = cfg.get("mock_value", "mock-token")

        if t == "apiKey":
            loc = cfg.get("in", "header")
            key_name = cfg.get("name", scheme_name)
            if loc == "header":
                return [f"-H '{key_name}: {mv}'"]
            elif loc == "query":
                return [f"# add query param: ?{key_name}={mv}"]
            elif loc == "cookie":
                return [f"-H 'Cookie: {key_name}={mv}'"]
        elif t == "http":
            if http_scheme == "bearer":
                return [f"-H 'Authorization: Bearer {mv}'"]
            elif http_scheme == "basic":
                user, pwd = (mv[0], mv[1]) if isinstance(mv, list) else ("mock-user", "mock-password")
                return [f"--user '{user}:{pwd}'"]
        elif t in ("oauth2", "openIdConnect"):
            return [f"-H 'Authorization: Bearer {mv}'"]
    return []


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def path_to_flask_rule(path: str) -> str:
    return re.sub(r"\{(\w+)\}", r"<\1>", path)


def get_base_path(spec: dict) -> str:
    servers = spec.get("servers")
    if servers:
        from urllib.parse import urlparse
        base = urlparse(servers[0].get("url", "")).path.rstrip("/")
        if base:
            return base
    return spec.get("basePath", "").rstrip("/")


def slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
    return slug or "mock-api"


# ---------------------------------------------------------------------------
# Auth middleware code generator
# ---------------------------------------------------------------------------

def generate_auth_section(schemes: Dict[str, dict], token_paths: Optional[List[str]] = None) -> List[str]:
    """Return lines of Python code for the auth block in mock_server.py."""
    if not schemes:
        return []

    # Paths that are always open (never gated by auth)
    always_open = ["/mock-control", "/mock-auth-status"] + (token_paths or [])
    always_open_repr = repr(always_open)

    schemes_repr = json.dumps(schemes, indent=4)
    schemes_indented = "\n".join("    " + l for l in schemes_repr.splitlines())

    lines = [
        "",
        "# ---------------------------------------------------------------------------",
        "# Authentication",
        "#",
        "# AUTH_ENFORCE = False  →  bypass mode: credentials are logged but never rejected",
        "# AUTH_ENFORCE = True   →  enforce mode: missing/wrong credentials return 401",
        "#",
        "# AUTH_SCHEMES is derived from the spec's securityDefinitions / securitySchemes.",
        "# Edit mock_value entries to match the credentials your client will send.",
        "# ---------------------------------------------------------------------------",
        "AUTH_ENFORCE: bool = False",
        "",
        f"AUTH_SCHEMES: dict ={schemes_indented}",
        "",
        "",
        "def _validate_scheme(cfg: dict) -> bool:",
        "    \"\"\"Return True if the current request satisfies this auth scheme.\"\"\"",
        "    import base64",
        "    t = cfg.get('type', '')",
        "    mv = cfg.get('mock_value', '')",
        "    http_scheme = cfg.get('scheme', '').lower()",
        "",
        "    if t == 'apiKey':",
        "        loc  = cfg.get('in', 'header')",
        "        name = cfg.get('name', '')",
        "        if loc == 'header':",
        "            return request.headers.get(name) == mv",
        "        if loc == 'query':",
        "            return request.args.get(name) == mv",
        "        if loc == 'cookie':",
        "            return request.cookies.get(name) == mv",
        "",
        "    if t == 'http':",
        "        auth = request.headers.get('Authorization', '')",
        "        if http_scheme == 'bearer':",
        "            return auth == f'Bearer {mv}'",
        "        if http_scheme == 'basic':",
        "            if isinstance(mv, list) and len(mv) == 2:",
        "                encoded = base64.b64encode(f'{mv[0]}:{mv[1]}'.encode()).decode()",
        "            else:",
        "                encoded = base64.b64encode(str(mv).encode()).decode()",
        "            return auth == f'Basic {encoded}'",
        "",
        "    if t in ('oauth2', 'openIdConnect'):",
        "        auth = request.headers.get('Authorization', '')",
        "        return auth == f'Bearer {mv}'",
        "",
        "    return False",
        "",
        "",
        "@app.before_request",
        "def check_auth():",
        "    \"\"\"Auth gate — runs before every request.\"\"\"",
        f"    if request.path.rstrip('/') in {always_open_repr}:",
        "        return  # token endpoints and control routes are always open",
        "",
        "    if not AUTH_SCHEMES:",
        "        return  # spec declares no security",
        "",
        "    # Log which credentials arrived (useful in bypass mode for debugging)",
        "    auth_header = request.headers.get('Authorization', '<none>')",
        "    api_key_headers = {k: v for k, v in request.headers if 'key' in k.lower() or 'token' in k.lower()}",
        "    app.logger.debug('AUTH  path=%s  Authorization=%s  extras=%s',",
        "                     request.path, auth_header, api_key_headers)",
        "",
        "    if not AUTH_ENFORCE:",
        "        return  # bypass — log only",
        "",
        "    # Any one scheme passing is sufficient",
        "    for cfg in AUTH_SCHEMES.values():",
        "        if _validate_scheme(cfg):",
        "            return",
        "",
        "    return jsonify({",
        "        'error': 'Unauthorized',",
        "        'hint': 'Set AUTH_ENFORCE=False in mock_server.py to bypass, '",
        "                'or send the correct credential from AUTH_SCHEMES.mock_value'",
        "    }), 401",
        "",
        "",
        "@app.route('/mock-auth-status', methods=['GET'])",
        "def mock_auth_status():",
        "    \"\"\"Introspect current auth config — GET /mock-auth-status\"\"\"",
        "    return jsonify({",
        "        'AUTH_ENFORCE': AUTH_ENFORCE,",
        "        'schemes': {",
        "            name: {",
        "                'type': cfg.get('type'),",
        "                'in':   cfg.get('in'),",
        "                'name': cfg.get('name'),",
        "                'scheme': cfg.get('scheme'),",
        "                'mock_value': cfg.get('mock_value'),",
        "            }",
        "            for name, cfg in AUTH_SCHEMES.items()",
        "        }",
        "    })",
        "",
    ]
    return lines


# ---------------------------------------------------------------------------
# Server code generator
# ---------------------------------------------------------------------------

def generate_server_code(
    spec: dict,
    selected_endpoints: Optional[List[str]] = None,
    port: int = 8080,
) -> str:
    all_endpoints = extract_endpoints(spec)

    if selected_endpoints:
        selected_set = set()
        for s in selected_endpoints:
            if ":" in s:
                m, p = s.split(":", 1)
                selected_set.add(f"{m.upper()}:{p}")
            else:
                selected_set.add(s.upper())
        all_endpoints = [ep for ep in all_endpoints if f"{ep['method']}:{ep['path']}" in selected_set]

    base_path = get_base_path(spec)
    title   = spec.get("info", {}).get("title", "Mock API")
    version = spec.get("info", {}).get("version", "1.0.0")
    schemes = extract_auth_schemes(spec)
    token_eps = extract_token_endpoints(schemes)
    token_paths = [te["flask_path"] for te in token_eps]

    lines = [
        "#!/usr/bin/env python3",
        f'"""Auto-generated mock server for: {title} v{version}"""',
        "",
        "from flask import Flask, jsonify, request",
        "import json",
        "",
        "app = Flask(__name__)",
        "app.logger.setLevel('DEBUG')",
        "",
        "# ---------------------------------------------------------------------------",
        "# Mock data registry — edit to override any response at startup",
        "# ---------------------------------------------------------------------------",
        "MOCK_RESPONSES: dict = {}",
        "",
    ]

    # Auth gate + token endpoints
    lines += generate_auth_section(schemes, token_paths=token_paths)
    lines += generate_token_endpoint_section(schemes)

    # Route functions
    seen_fn_names: set = set()

    for ep in all_endpoints:
        method    = ep["method"]
        path      = ep["path"]
        operation = ep["operation"]
        body, status = build_mock_response(operation, spec)

        flask_path = path_to_flask_rule(base_path + path)
        op_id   = operation.get("operationId") or f"{method}_{path}"
        fn_name = re.sub(r"[^a-zA-Z0-9_]", "_", op_id).lower()
        orig    = fn_name
        counter = 1
        while fn_name in seen_fn_names:
            fn_name = f"{orig}_{counter}"
            counter += 1
        seen_fn_names.add(fn_name)

        summary = operation.get("summary", "")

        # Embed the body as a JSON string parsed at runtime — avoids Python
        # true/false/null vs JSON true/false/null mismatch.
        body_json = json.dumps(body, indent=4)
        body_json_escaped = body_json.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
        body_lines_indented = "\n".join("    " + l for l in body_json_escaped.splitlines())

        lines += [
            "",
            f"# {method} {path}" + (f" — {summary}" if summary else ""),
            f'@app.route("{flask_path}", methods=["{method}"])',
            f"def {fn_name}(**kwargs):",
            f"    mock_key = '{method}:{path}'",
            "    if mock_key in MOCK_RESPONSES:",
            "        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)",
            f"    body = json.loads(\"\"\"",
            body_lines_indented,
            "    \"\"\")",
            f"    return jsonify(body), {status}",
            "",
        ]

    lines += [
        "",
        "# ---------------------------------------------------------------------------",
        "# Runtime controls",
        "# ---------------------------------------------------------------------------",
        "",
        "# POST /mock-control — override any response without restarting",
        "# Body: {\"key\": \"GET:/users\", \"response\": {...}, \"status\": 200}",
        '@app.route("/mock-control", methods=["POST"])',
        "def mock_control():",
        "    data = request.get_json(force=True)",
        "    key  = data.get('key')",
        "    if not key:",
        "        return jsonify({'error': 'key required'}), 400",
        "    MOCK_RESPONSES[key] = data.get('response', {})",
        "    MOCK_RESPONSES[key + '__status'] = data.get('status', 200)",
        "    return jsonify({'ok': True, 'key': key}), 200",
        "",
        "",
        "if __name__ == '__main__':",
        f"    print('Mock server for \"{title}\" running on http://localhost:{port}')",
        f"    app.run(host='0.0.0.0', port={port}, debug=True)",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# requirements.txt
# ---------------------------------------------------------------------------

def generate_requirements(is_yaml: bool) -> str:
    lines = ["flask>=3.0,<4"]
    if is_yaml:
        lines.append("pyyaml>=6.0,<7")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# QUICKSTART.md
# ---------------------------------------------------------------------------

def generate_quickstart(
    spec: dict,
    endpoints: List[dict],
    port: int,
    out_dir: str,
    is_yaml: bool,
) -> str:
    title    = spec.get("info", {}).get("title", "Mock API")
    version  = spec.get("info", {}).get("version", "1.0.0")
    base_path = get_base_path(spec)
    base_url  = f"http://localhost:{port}"
    schemes   = extract_auth_schemes(spec)

    # ---- auth section -------------------------------------------------------
    token_eps = extract_token_endpoints(schemes)
    has_oauth = bool(token_eps)

    # Build token-acquisition block (Step 1) for OAuth2/openIdConnect schemes
    token_step = ""
    if has_oauth:
        token_blocks = []
        for te in token_eps:
            token_url  = f"{base_url}{te['flask_path']}"
            # Replace Flask <param> back to example value for curl
            token_url_ex = re.sub(r"<(\w+)>", "your-tenant-id", token_url)
            scope_str  = list(te["scopes"].keys())[0] if te["scopes"] else "api://default"
            grant      = te["grant_type"]
            token_blocks.append(
                f"```bash\n"
                f"# Scheme: {te['scheme_name']} ({te['flow_type']})\n"
                f"# Mirrors real token URL: {te['original_url']}\n"
                f"TOKEN=$(curl -s -X POST '{token_url_ex}' \\\n"
                f"  -d 'client_id=<your-app-id>' \\\n"
                f"  -d 'client_secret=<your-client-secret>' \\\n"
                f"  -d 'grant_type={grant}' \\\n"
                f"  -d 'scope={scope_str}' \\\n"
                f"  | python3 -c \"import sys,json; print(json.load(sys.stdin)['access_token'])\")\n"
                f"echo \"Token acquired: $TOKEN\"\n"
                f"```"
            )
        token_step = (
            "## Authentication — real two-step OAuth2 flow\n\n"
            "This API uses OAuth2. The real client flow is:\n\n"
            "1. **Step 1** — POST `client_id` + `client_secret` + `grant_type` to the identity provider → receive `access_token`\n"
            "2. **Step 2** — Send `Authorization: Bearer <access_token>` with every API call\n\n"
            "The mock server simulates **both steps**. The token endpoint is hosted locally "
            "at the same path as the real provider (host stripped), so client code only needs "
            "to change the base URL. Any `client_id` / `client_secret` is accepted.\n\n"
            "### Step 1 — Acquire a mock token\n\n"
            + "\n\n".join(token_blocks)
            + "\n\n"
            "> The returned `access_token` is pre-wired to work with all mocked API endpoints below.\n\n"
            "### Step 2 — Use `$TOKEN` in API calls\n\n"
            "All curl examples in section 4 use `$TOKEN` from Step 1. "
            "Run Step 1 first in the same shell session.\n\n"
            f"Inspect the current auth config at any time:\n"
            f"```bash\ncurl -s '{base_url}/mock-auth-status' | python3 -m json.tool\n```\n\n"
            "**Bypass vs enforce mode:**\n\n"
            "| `AUTH_ENFORCE` | Behaviour |\n"
            "|---|---|\n"
            "| `False` (default) | All requests pass; credentials are logged but not checked |\n"
            "| `True` | Token from Step 1 required; wrong/missing token → `401` |\n\n"
            "Toggle in `mock_server.py`: `AUTH_ENFORCE = True`\n"
        )
    elif schemes:
        auth_rows = []
        for name, cfg in schemes.items():
            t        = cfg.get("type", "")
            http_s   = cfg.get("scheme", "")
            mv       = cfg.get("mock_value", "")
            loc      = cfg.get("in", "")
            key_name = cfg.get("name", name)
            if t == "apiKey":
                ex = f"`-H '{key_name}: {mv}'`" if loc == "header" else f"`?{key_name}={mv}`"
                auth_rows.append(f"| `{name}` | API Key ({loc}) | `{key_name}` | `{mv}` | {ex} |")
            elif t == "http" and http_s == "bearer":
                auth_rows.append(f"| `{name}` | Bearer Token | `Authorization` | `Bearer {mv}` | `-H 'Authorization: Bearer {mv}'` |")
            elif t == "http" and http_s == "basic":
                u, p = (mv[0], mv[1]) if isinstance(mv, list) else ("mock-user", "mock-password")
                auth_rows.append(f"| `{name}` | Basic Auth | `Authorization` | `{u}:{p}` | `--user '{u}:{p}'` |")
        token_step = (
            "## Authentication\n\n"
            "The mock server runs in **bypass mode** (`AUTH_ENFORCE = False`) by default. "
            "Set `AUTH_ENFORCE = True` in `mock_server.py` to enforce credentials.\n\n"
            "| Scheme | Type | Header / Param | Mock credential | curl flag |\n"
            "|--------|------|---------------|-----------------|----------|\n"
            + "\n".join(auth_rows)
            + f"\n\n```bash\ncurl -s '{base_url}/mock-auth-status' | python3 -m json.tool\n```\n"
        )

    # ---- curl examples — use $TOKEN variable for OAuth2 schemes -------------
    curl_examples = []
    for ep in endpoints:
        method    = ep["method"]
        path      = ep["path"]
        operation = ep["operation"]
        summary   = operation.get("summary", "")
        url_path  = re.sub(r"\{(\w+)\}", "1", base_path + path)
        url       = f"{base_url}{url_path}"

        # For OAuth2/openIdConnect use $TOKEN shell variable; others use literal value
        raw_flags = auth_curl_flags(operation, spec, schemes)
        if has_oauth and raw_flags:
            auth_str = " \\\n  -H \"Authorization: Bearer $TOKEN\""
        elif raw_flags:
            auth_str = " \\\n  " + " \\\n  ".join(raw_flags)
        else:
            auth_str = ""

        if method in ("POST", "PUT", "PATCH"):
            body, _ = build_mock_response(operation, spec)
            body_str = json.dumps(body, indent=2)
            cmd = (
                f"# {method} {path}" + (f" — {summary}" if summary else "") + "\n"
                f"curl -s -X {method} '{url}'{auth_str} \\\n"
                f"  -H 'Content-Type: application/json' \\\n"
                f"  -d '{body_str}'"
            )
        else:
            cmd = (
                f"# {method} {path}" + (f" — {summary}" if summary else "") + "\n"
                f"curl -s '{url}'{auth_str}"
            )
        curl_examples.append(cmd)

    curl_block = "\n\n".join(curl_examples)

    endpoint_list = "\n".join(
        f"- `{ep['method']} {base_path}{ep['path']}`"
        + (f" — {ep['operation'].get('summary', '')}" if ep['operation'].get('summary') else "")
        for ep in endpoints
    )

    deps_note = f"> `requirements.txt` includes: flask" + (", pyyaml" if is_yaml else "")

    return f"""# Quick Start — {title} Mock Server

Auto-generated mock server for **{title} v{version}**, running on port **{port}**.

## Prerequisites

- Python 3.9+
- pip

## 1. Install dependencies

```bash
cd {out_dir}
pip install -r requirements.txt
```

{deps_note}

## 2. Start the server

```bash
python mock_server.py
```

Expected output:

```
Mock server for "{title}" running on http://localhost:{port}
 * Running on http://0.0.0.0:{port}
```

## 3. Mocked endpoints

{endpoint_list}

{token_step}
## 4. Send queries

{curl_block}

## 5. Override a response at runtime

Swap in any body or status code without restarting:

```bash
curl -s -X POST '{base_url}/mock-control' \\
  -H 'Content-Type: application/json' \\
  -d '{{"key": "{endpoints[0]["method"] if endpoints else "GET"}:{endpoints[0]["path"] if endpoints else "/example"}", "response": {{"error": "Service unavailable"}}, "status": 503}}'
```

## 6. Debug checklist

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `Connection refused` | Server not running | Run `python mock_server.py` |
| `Address already in use` | Port {port} taken | Use `--port <other>` or `lsof -i :{port}` to find the process |
| `401 Unauthorized` | `AUTH_ENFORCE=True` with wrong/missing credential | Send the `mock_value` from `AUTH_SCHEMES`, or set `AUTH_ENFORCE=False` |
| `404 Not Found` | Wrong path or base path missing | Check base path prefix — all routes start with `{base_path or "/"}` |
| `ModuleNotFoundError: flask` | Dependencies not installed | `pip install -r requirements.txt` |
| Unexpected response body | `MOCK_RESPONSES` override active | `POST /mock-control` with the correct key to reset, or restart |

## 7. Customise responses

- **Edit at startup**: modify the `body = ...` literal inside any route function in `mock_server.py`.
- **Edit the registry**: update `MOCK_RESPONSES` dict at the top of `mock_server.py`.
- **Edit at runtime**: `POST /mock-control` (no restart needed).
- **Toggle auth enforcement**: change `AUTH_ENFORCE = True/False` in `mock_server.py`.
"""


# ---------------------------------------------------------------------------
# Output directory builder
# ---------------------------------------------------------------------------

def build_output_dir(
    spec: dict,
    spec_path: str,
    selected_endpoints: Optional[List[str]],
    port: int,
    base_out: Optional[str],
) -> str:
    """Create the output folder and write all three files. Returns the folder path."""
    title    = spec.get("info", {}).get("title", "Mock API")
    dir_name = slugify(title)
    out_dir  = (Path(base_out) if base_out else Path(spec_path).parent) / dir_name
    out_dir.mkdir(parents=True, exist_ok=True)

    all_endpoints = extract_endpoints(spec)
    if selected_endpoints:
        selected_set = set()
        for s in selected_endpoints:
            if ":" in s:
                m, p = s.split(":", 1)
                selected_set.add(f"{m.upper()}:{p}")
            else:
                selected_set.add(s.upper())
        mocked = [ep for ep in all_endpoints if f"{ep['method']}:{ep['path']}" in selected_set]
    else:
        mocked = all_endpoints

    is_yaml = spec_path.endswith((".yaml", ".yml"))

    (out_dir / "mock_server.py").write_text(
        generate_server_code(spec, selected_endpoints=selected_endpoints, port=port)
    )
    (out_dir / "requirements.txt").write_text(generate_requirements(is_yaml))
    (out_dir / "QUICKSTART.md").write_text(
        generate_quickstart(spec, mocked, port, str(out_dir), is_yaml)
    )
    return str(out_dir)


# ---------------------------------------------------------------------------
# Smoke test — start server, probe every endpoint, report, kill
# ---------------------------------------------------------------------------

def _wait_for_server(base_url: str, timeout: int = 10) -> bool:
    """Poll base_url/mock-auth-status until server responds or timeout."""
    probe = f"{base_url}/mock-auth-status"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(probe, timeout=1)
            return True
        except Exception:
            time.sleep(0.3)
    return False


def smoke_test(out_dir: str, spec: dict, selected_endpoints: Optional[List[str]], port: int) -> int:
    """
    Start mock_server.py as a subprocess, probe every mocked endpoint,
    print results, kill the server.  Returns exit code (0 = all pass).
    """
    server_py   = str(Path(out_dir) / "mock_server.py")
    base_url    = f"http://localhost:{port}"
    base_path   = get_base_path(spec)
    schemes     = extract_auth_schemes(spec)

    all_endpoints = extract_endpoints(spec)
    if selected_endpoints:
        selected_set = set()
        for s in selected_endpoints:
            if ":" in s:
                m, p = s.split(":", 1)
                selected_set.add(f"{m.upper()}:{p}")
            else:
                selected_set.add(s.upper())
        mocked = [ep for ep in all_endpoints if f"{ep['method']}:{ep['path']}" in selected_set]
    else:
        mocked = all_endpoints

    print(f"\n{'='*60}")
    print(f"  SMOKE TEST — {spec.get('info', {}).get('title', 'Mock API')}")
    print(f"{'='*60}")
    print(f"  Starting server on port {port}...")

    proc = subprocess.Popen(
        [sys.executable, server_py],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if not _wait_for_server(base_url):
        proc.kill()
        out, err = proc.communicate()
        print("  ERROR: server did not start within 10 seconds.")
        print("  --- stdout ---")
        print(out.decode(errors="replace"))
        print("  --- stderr ---")
        print(err.decode(errors="replace"))
        return 1

    print(f"  Server ready at {base_url}\n")

    # ---- Step 1: acquire a mock token for OAuth2/openIdConnect schemes ------
    token_eps = extract_token_endpoints(schemes)
    live_tokens: Dict[str, str] = {}   # scheme_name → access_token
    token_results = []
    for te in token_eps:
        token_url_path = re.sub(r"<(\w+)>", "mock-tenant-id", te["flask_path"])
        token_url      = f"{base_url}{token_url_path}"
        scope_str      = list(te["scopes"].keys())[0] if te["scopes"] else "api://default"
        post_body      = (
            f"client_id=mock-app-id&client_secret=mock-secret"
            f"&grant_type={te['grant_type']}&scope={scope_str}"
        ).encode()
        try:
            req = urllib.request.Request(
                token_url,
                data=post_body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                token_data = json.loads(resp.read())
                live_tokens[te["scheme_name"]] = token_data.get("access_token", "")
            token_results.append(("PASS", "TOKEN", te["flask_path"], "200"))
        except Exception as e:
            token_results.append(("FAIL", "TOKEN", te["flask_path"], str(e)))

    passed = 0
    failed = 0
    results = []

    for ep in mocked:
        method = ep["method"]
        path   = ep["path"]
        url_path = re.sub(r"\{(\w+)\}", "1", base_path + path)
        url = f"{base_url}{url_path}"

        # Use the live token acquired above for OAuth2; fall back to raw auth_curl_flags
        op_security = ep["operation"].get("security") or spec.get("security", [])
        auth_flags = auth_curl_flags(ep["operation"], spec, schemes)
        for sec_req in op_security:
            if not sec_req:
                break
            sname = next(iter(sec_req))
            if sname in live_tokens:
                auth_flags = [f"-H 'Authorization: Bearer {live_tokens[sname]}'"]
                break

        # Build curl command list
        cmd = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-X", method]
        for flag in auth_flags:
            # Parse flag string into tokens (basic parsing)
            flag = flag.strip()
            if flag.startswith("-H "):
                cmd += ["-H", flag[3:].strip("'\"")]
            elif flag.startswith("--user "):
                cmd += ["--user", flag[7:].strip("'\"")]
        cmd.append(url)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            status_code = result.stdout.strip()
            ok = status_code.startswith("2")
            symbol = "PASS" if ok else "FAIL"
            if ok:
                passed += 1
            else:
                failed += 1
            results.append((symbol, method, path, status_code))
        except subprocess.TimeoutExpired:
            failed += 1
            results.append(("FAIL", method, path, "TIMEOUT"))
        except FileNotFoundError:
            # curl not available — use urllib
            try:
                req = urllib.request.Request(url, method=method)
                with urllib.request.urlopen(req, timeout=5) as resp:
                    code = str(resp.status)
                ok = code.startswith("2")
                symbol = "PASS" if ok else "FAIL"
                if ok: passed += 1
                else:  failed += 1
                results.append((symbol, method, path, code))
            except urllib.error.HTTPError as e:
                failed += 1
                results.append(("FAIL", method, path, str(e.code)))
            except Exception as e:
                failed += 1
                results.append(("FAIL", method, path, str(e)))

    proc.kill()
    proc.wait()

    # Report — token probes first, then API endpoint probes
    all_results = token_results + results
    col_w = max((len(r[2]) for r in all_results), default=20) + 2
    if token_results:
        print("  -- token endpoint(s) --")
        for symbol, method, path, code in token_results:
            status = f"HTTP {code}" if code.isdigit() else code
            print(f"  [{symbol}]  {method:<7} {path:<{col_w}}  {status}")
            if symbol == "PASS": passed += 1
            else:                failed += 1
        print("  -- api endpoint(s) --")
    for symbol, method, path, code in results:
        print(f"  [{symbol}]  {method:<7} {path:<{col_w}}  HTTP {code}")

    print(f"\n  Result: {passed + sum(1 for r in results if r[0]=='PASS')} passed, "
          f"{failed + sum(1 for r in results if r[0]=='FAIL')} failed")
    print(f"{'='*60}\n")
    return 0 if (failed == 0 and all(r[0] == "PASS" for r in results)) else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a Flask mock server folder from an OpenAPI spec."
    )
    parser.add_argument("spec", help="Path to OpenAPI spec file (.json, .yaml, .yml)")
    parser.add_argument(
        "--endpoints", nargs="*", metavar="METHOD:/path",
        help="Only mock these endpoints (e.g. GET:/users POST:/users/{id}). Omit for ALL.",
    )
    parser.add_argument("--port", type=int, default=8080, help="HTTP port (default: 8080)")
    parser.add_argument(
        "--out-dir", default=None,
        help="Parent directory for the generated folder (default: spec file directory).",
    )
    parser.add_argument(
        "--run", action="store_true",
        help="Generate the folder AND immediately start the server (replaces current process).",
    )
    parser.add_argument(
        "--smoke-test", action="store_true",
        help="Generate the folder, start the server, probe every endpoint, report, then exit.",
    )
    args = parser.parse_args()

    if not Path(args.spec).exists():
        print(f"ERROR: spec file not found: {args.spec}")
        sys.exit(1)

    spec    = load_spec(args.spec)
    out_dir = build_output_dir(
        spec=spec,
        spec_path=args.spec,
        selected_endpoints=args.endpoints,
        port=args.port,
        base_out=args.out_dir,
    )

    print(f"Generated folder : {out_dir}/")
    print(f"  mock_server.py   — Flask HTTP server")
    print(f"  requirements.txt — pinned dependencies")
    print(f"  QUICKSTART.md    — setup & usage guide")

    schemes = extract_auth_schemes(spec)
    if schemes:
        print(f"\n  Auth schemes detected: {', '.join(schemes.keys())}")
        print(f"  AUTH_ENFORCE = False (bypass mode) — edit mock_server.py to enforce")

    print(f"\nTo start:")
    print(f"  cd {out_dir}")
    print(f"  pip install -r requirements.txt")
    print(f"  python mock_server.py")

    if args.smoke_test:
        try:
            import flask  # noqa: F401
        except ImportError:
            os.system(f"{sys.executable} -m pip install flask -q")
        sys.exit(smoke_test(out_dir, spec, args.endpoints, args.port))

    if args.run:
        try:
            import flask  # noqa: F401
        except ImportError:
            os.system(f"{sys.executable} -m pip install flask -q")
        os.execv(sys.executable, [sys.executable, str(Path(out_dir) / "mock_server.py")])


if __name__ == "__main__":
    main()

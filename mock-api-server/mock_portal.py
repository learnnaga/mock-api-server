#!/usr/bin/env python3
"""
Mock API Portal — unified Swagger UI for all generated mock servers.

Runs on port 8888. For each registered mock server:
  - Displays a status card on the homepage
  - Serves a rewritten OpenAPI spec via /api/spec/<slug> (servers[] → /proxy/<slug>)
  - Serves Swagger UI at /swagger/<slug> with auto-filled auth credentials
  - Proxies all Try-It-Out calls via /proxy/<slug>/... to the live mock server

Usage:
    pip install flask requests
    python mock_portal.py

portal-config.json (sibling file) registers mock servers. Re-read on every
request so adding a new mock only requires updating the JSON + restarting
the portal.
"""

import copy
import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

import requests
from flask import Flask, jsonify, make_response, request

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PORTAL_PORT  = 8888
PORTAL_ROOT  = Path(__file__).parent
CONFIG_FILE  = PORTAL_ROOT / "portal-config.json"

HOP_BY_HOP = frozenset({
    "transfer-encoding", "connection", "keep-alive",
    "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "upgrade",
})

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def load_config() -> dict:
    with open(CONFIG_FILE) as f:
        return json.load(f)


def get_mock(slug: str) -> Optional[dict]:
    return next((m for m in load_config()["mocks"] if m["slug"] == slug), None)

# ---------------------------------------------------------------------------
# Spec rewriter — rewrites servers[] and tokenUrl so Swagger UI
# routes all Try-It-Out calls through /proxy/<slug>/...
# ---------------------------------------------------------------------------

def _rewrite_spec(spec: dict, slug: str) -> dict:
    import re
    from urllib.parse import urlparse

    def _resolve_path(url: str) -> str:
        """Extract path from URL and replace any {param} placeholders with
        concrete mock values so Swagger UI can call the endpoint directly."""
        path = urlparse(url).path
        # Replace all {param} placeholders — Flask mock accepts any value
        path = re.sub(r"\{[^}]+\}", "mock-tenant-id", path)
        return path

    s = copy.deepcopy(spec)
    proxy_base = f"http://localhost:{PORTAL_PORT}/proxy/{slug}"

    if "openapi" in s:
        # OpenAPI 3.x
        s["servers"] = [{"url": proxy_base, "description": f"Portal proxy → {slug}"}]
        for scheme in s.get("components", {}).get("securitySchemes", {}).values():
            if scheme.get("type") == "oauth2":
                for flow in scheme.get("flows", {}).values():
                    if "tokenUrl" in flow:
                        flow["tokenUrl"] = proxy_base + _resolve_path(flow["tokenUrl"])
                    if "authorizationUrl" in flow:
                        flow["authorizationUrl"] = proxy_base + _resolve_path(flow["authorizationUrl"])
    elif "swagger" in s:
        # Swagger 2.x
        s["host"]     = f"localhost:{PORTAL_PORT}"
        s["basePath"] = f"/proxy/{slug}"
        s["schemes"]  = ["http"]
        for scheme in s.get("securityDefinitions", {}).values():
            if scheme.get("type") == "oauth2":
                if "tokenUrl" in scheme:
                    scheme["tokenUrl"] = f"http://localhost:{PORTAL_PORT}/proxy/{slug}{_resolve_path(scheme['tokenUrl'])}"

    return s

# ---------------------------------------------------------------------------
# Routes — homepage
# ---------------------------------------------------------------------------

@app.route("/")
def homepage():
    config = load_config()
    cards_html = ""
    for m in config["mocks"]:
        slug    = m["slug"]
        title   = m["title"]
        version = m["version"]
        port    = m["port"]
        enforce = m.get("auth_enforce", False)

        scheme_badges = ""
        for s in m.get("auth_schemes", []):
            stype = s["type"]
            if stype == "apiKey":
                badge_text = f"API Key · {s['param_name']}"
                badge_cls  = "badge-apikey"
            elif stype == "oauth2":
                badge_text = "OAuth2 · client_credentials"
                badge_cls  = "badge-oauth"
            elif stype == "http":
                badge_text = "HTTP Bearer"
                badge_cls  = "badge-bearer"
            else:
                badge_text = stype
                badge_cls  = "badge-other"
            scheme_badges += f'<span class="badge {badge_cls}">{badge_text}</span>'

        enforce_badge = (
            '<span class="badge badge-enforcing">Auth Enforced</span>'
            if enforce else
            '<span class="badge badge-bypass">Auth Bypass</span>'
        )

        cards_html += f"""
        <div class="card" id="card-{slug}">
          <div class="card-header">
            <span class="status-dot" id="dot-{slug}" title="Checking..."></span>
            <div class="card-title">
              <h2>{title}</h2>
              <span class="version">v{version}</span>
            </div>
            <span class="port-badge">:{port}</span>
          </div>
          <div class="card-badges">
            {scheme_badges}
            {enforce_badge}
          </div>
          <div class="card-actions">
            <a class="btn btn-primary" href="/swagger/{slug}" target="_blank">Open Swagger UI</a>
            <a class="btn btn-secondary" href="/api/spec/{slug}" target="_blank">Raw Spec</a>
          </div>
          <div class="auth-hint" id="hint-{slug}"></div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mock API Portal</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0f172a; color: #e2e8f0; min-height: 100vh;
    }}
    header {{
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      border-bottom: 1px solid #334155;
      padding: 24px 32px; display: flex; align-items: center; gap: 16px;
    }}
    header svg {{ flex-shrink: 0; }}
    header h1 {{ margin: 0; font-size: 1.5rem; font-weight: 700; color: #f8fafc; }}
    header p  {{ margin: 4px 0 0; font-size: 0.875rem; color: #94a3b8; }}
    main {{ padding: 32px; max-width: 1200px; margin: 0 auto; }}
    .grid {{
      display: grid; gap: 20px;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    }}
    .card {{
      background: #1e293b; border: 1px solid #334155; border-radius: 12px;
      padding: 20px; display: flex; flex-direction: column; gap: 12px;
      transition: border-color .2s, box-shadow .2s;
    }}
    .card:hover {{ border-color: #4f46e5; box-shadow: 0 0 0 1px #4f46e5; }}
    .card-header {{ display: flex; align-items: center; gap: 10px; }}
    .status-dot {{
      width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
      background: #475569; transition: background .3s;
    }}
    .status-dot.up   {{ background: #22c55e; box-shadow: 0 0 6px #22c55e88; }}
    .status-dot.down {{ background: #ef4444; box-shadow: 0 0 6px #ef444488; }}
    .card-title {{ flex: 1; }}
    .card-title h2 {{ margin: 0; font-size: 1rem; font-weight: 600; color: #f1f5f9; }}
    .version {{ font-size: 0.75rem; color: #64748b; }}
    .port-badge {{
      font-size: 0.75rem; font-weight: 600; padding: 2px 8px;
      background: #0f172a; border: 1px solid #334155; border-radius: 20px; color: #94a3b8;
    }}
    .card-badges {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .badge {{
      font-size: 0.7rem; font-weight: 500; padding: 3px 8px;
      border-radius: 20px; border: 1px solid transparent;
    }}
    .badge-apikey    {{ background: #1e3a5f; border-color: #3b82f6; color: #93c5fd; }}
    .badge-oauth     {{ background: #2e1065; border-color: #8b5cf6; color: #c4b5fd; }}
    .badge-bearer    {{ background: #1e3a5f; border-color: #06b6d4; color: #67e8f9; }}
    .badge-other     {{ background: #1f2937; border-color: #6b7280; color: #d1d5db; }}
    .badge-enforcing {{ background: #450a0a; border-color: #ef4444; color: #fca5a5; }}
    .badge-bypass    {{ background: #1c1917; border-color: #6b7280; color: #9ca3af; }}
    .card-actions {{ display: flex; gap: 8px; }}
    .btn {{
      padding: 8px 16px; border-radius: 6px; font-size: 0.875rem; font-weight: 500;
      text-decoration: none; text-align: center; transition: opacity .15s;
    }}
    .btn:hover {{ opacity: .85; }}
    .btn-primary   {{ background: #4f46e5; color: #fff; }}
    .btn-secondary {{ background: #1e293b; border: 1px solid #334155; color: #94a3b8; }}
    .auth-hint {{
      font-size: 0.75rem; color: #64748b; padding: 8px; background: #0f172a;
      border-radius: 6px; font-family: monospace; display: none;
    }}
    .auth-hint.visible {{ display: block; }}
    footer {{
      text-align: center; padding: 24px; color: #475569; font-size: 0.8rem;
      border-top: 1px solid #1e293b;
    }}
  </style>
</head>
<body>
  <header>
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
      <rect width="36" height="36" rx="8" fill="#4f46e5"/>
      <path d="M10 18h16M10 12h10M10 24h13" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/>
    </svg>
    <div>
      <h1>Mock API Portal</h1>
      <p>Unified Swagger UI for all mock servers &mdash; running on port {PORTAL_PORT}</p>
    </div>
  </header>
  <main>
    <div class="grid">
      {cards_html}
    </div>
  </main>
  <footer>Mock API Portal &mdash; generated by mock-api-server skill</footer>
  <script>
    async function refreshStatus() {{
      try {{
        const res = await fetch('/api/status');
        const data = await res.json();
        for (const [slug, info] of Object.entries(data)) {{
          const dot = document.getElementById('dot-' + slug);
          if (!dot) continue;
          dot.classList.remove('up', 'down');
          dot.classList.add(info.up ? 'up' : 'down');
          dot.title = info.up ? 'Running on :' + info.port : 'Offline (start: python mock_server.py)';
          const hint = document.getElementById('hint-' + slug);
          if (hint && !info.up) {{
            hint.textContent = 'Server offline — cd ' + slug + ' && python mock_server.py';
            hint.classList.add('visible');
          }}
        }}
      }} catch(e) {{ console.error('status check failed', e); }}
    }}
    refreshStatus();
    setInterval(refreshStatus, 10000);
  </script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Routes — liveness status for all mocks
# ---------------------------------------------------------------------------

@app.route("/api/status")
def api_status():
    config  = load_config()
    results = {}
    for m in config["mocks"]:
        slug = m["slug"]
        port = m["port"]
        try:
            urllib.request.urlopen(
                f"http://localhost:{port}/mock-auth-status", timeout=1
            )
            results[slug] = {"up": True, "port": port}
        except Exception:
            results[slug] = {"up": False, "port": port}
    return jsonify(results)

# ---------------------------------------------------------------------------
# Routes — rewritten OpenAPI spec
# ---------------------------------------------------------------------------

@app.route("/api/spec/<slug>")
def api_spec(slug):
    entry = get_mock(slug)
    if not entry:
        return jsonify({"error": f"No mock registered for slug '{slug}'"}), 404

    spec_path = PORTAL_ROOT / entry["dir"] / "openapi.json"
    if not spec_path.exists():
        return jsonify({"error": f"openapi.json not found in {entry['dir']}"}), 404

    with open(spec_path) as f:
        spec = json.load(f)

    rewritten = _rewrite_spec(spec, slug)
    resp = make_response(json.dumps(rewritten, indent=2))
    resp.headers["Content-Type"] = "application/json"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

# ---------------------------------------------------------------------------
# Routes — Swagger UI
# ---------------------------------------------------------------------------

@app.route("/swagger/<slug>")
def swagger_ui(slug):
    entry = get_mock(slug)
    if not entry:
        return f"<h1>404</h1><p>No mock registered for slug '{slug}'</p>", 404

    title          = entry["title"]
    auth_schemes   = entry.get("auth_schemes", [])
    schemes_json   = json.dumps({s["name"]: s for s in auth_schemes})

    # Build preauth JS calls injected into onComplete (for apiKey schemes)
    preauth_calls = []
    has_oauth2    = False
    for s in auth_schemes:
        name = s["name"]
        mv   = s.get("mock_value", "")
        if s["type"] == "apiKey":
            preauth_calls.append(
                f'ui.preauthorizeApiKey({json.dumps(name)}, {json.dumps(mv)});'
            )
        elif s["type"] in ("oauth2", "openIdConnect"):
            has_oauth2 = True
    preauth_js = "\n          ".join(preauth_calls) if preauth_calls else "/* no auth */"

    # For OAuth2: use MutationObserver to auto-fill client_id / client_secret
    # whenever the Authorize dialog opens (Swagger UI renders it dynamically)
    oauth2_prefill_js = ""
    if has_oauth2:
        oauth2_prefill_js = """
    // Auto-fill mock OAuth2 credentials whenever the Authorize dialog opens
    const MOCK_CLIENT_ID     = "mock-client-id";
    const MOCK_CLIENT_SECRET = "mock-client-secret";
    const observer = new MutationObserver(() => {
      const fill = (selector, value) => {
        const el = document.querySelector(selector);
        if (el && !el.value) {
          el.value = value;
          el.dispatchEvent(new Event('input',  { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
        }
      };
      fill('input[data-name="client_id"]',     MOCK_CLIENT_ID);
      fill('input[data-name="client_secret"]', MOCK_CLIENT_SECRET);
    });
    observer.observe(document.body, { childList: true, subtree: true });
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Mock API Portal</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
  <style>
    body {{ margin: 0; }}
    .topbar-back {{
      background: #1e293b; padding: 10px 20px; display: flex;
      align-items: center; gap: 12px; border-bottom: 1px solid #334155;
    }}
    .topbar-back a {{
      color: #94a3b8; text-decoration: none; font-size: 0.85rem;
      font-family: -apple-system, sans-serif;
    }}
    .topbar-back a:hover {{ color: #e2e8f0; }}
    .topbar-back span {{ color: #475569; }}
    .topbar-back strong {{ color: #e2e8f0; font-family: -apple-system, sans-serif; }}
  </style>
</head>
<body>
  <div class="topbar-back">
    <a href="/">&larr; Portal Home</a>
    <span>/</span>
    <strong>{title}</strong>
  </div>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    const ui = SwaggerUIBundle({{
      url: "/api/spec/{slug}",
      dom_id: "#swagger-ui",
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
      layout: "BaseLayout",
      deepLinking: true,
      tryItOutEnabled: true,
      requestInterceptor: (req) => {{
        // Belt-and-suspenders: ensure all requests go through the proxy
        if (req.url && !req.url.includes('/proxy/')) {{
          console.warn('[portal] unexpected direct request intercepted:', req.url);
        }}
        return req;
      }},
      onComplete: () => {{
        const schemes = {schemes_json};
        {preauth_js}
      }}
    }});
    {oauth2_prefill_js}
  </script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Routes — proxy
# ---------------------------------------------------------------------------

@app.route("/proxy/<slug>/", defaults={"subpath": ""},
           methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
@app.route("/proxy/<slug>/<path:subpath>",
           methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
def proxy(slug, subpath):
    entry = get_mock(slug)
    if not entry:
        return jsonify({"error": f"No mock registered for slug '{slug}'"}), 404

    target_url = f"http://localhost:{entry['port']}/{subpath}"
    if request.query_string:
        target_url += "?" + request.query_string.decode("utf-8")

    # Forward headers — strip hop-by-hop and Host
    fwd_headers = {
        k: v for k, v in request.headers
        if k.lower() not in HOP_BY_HOP and k.lower() != "host"
    }

    try:
        mock_resp = requests.request(
            method=request.method,
            url=target_url,
            headers=fwd_headers,
            data=request.get_data(),
            allow_redirects=False,
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Mock server is not running",
            "hint": f"cd {entry['dir']} && python mock_server.py",
            "target": target_url,
        }), 502
    except requests.exceptions.Timeout:
        return jsonify({"error": "Mock server timed out", "target": target_url}), 504

    # Forward response — strip hop-by-hop and let Flask set Content-Length
    excluded = HOP_BY_HOP | {"content-encoding", "content-length"}
    resp_headers = {
        k: v for k, v in mock_resp.headers.items()
        if k.lower() not in excluded
    }
    # Allow Swagger UI (same origin) to read the response
    resp_headers["Access-Control-Allow-Origin"]  = "*"
    resp_headers["Access-Control-Allow-Headers"] = "*"
    resp_headers["Access-Control-Allow-Methods"] = "*"

    return mock_resp.content, mock_resp.status_code, resp_headers


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"\nMock API Portal running on http://localhost:{PORTAL_PORT}")
    print(f"  Homepage:  http://localhost:{PORTAL_PORT}/")
    config = load_config()
    for m in config["mocks"]:
        print(f"  {m['title']:45s}  http://localhost:{PORTAL_PORT}/swagger/{m['slug']}")
    print()
    app.run(host="0.0.0.0", port=PORTAL_PORT, debug=False)

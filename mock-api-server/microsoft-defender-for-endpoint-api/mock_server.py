#!/usr/bin/env python3
"""Auto-generated mock server for: Microsoft Defender for Endpoint API v2.0.0"""

from flask import Flask, jsonify, request
import json

app = Flask(__name__)
app.logger.setLevel('DEBUG')

# ---------------------------------------------------------------------------
# Mock data registry — edit to override any response at startup
# ---------------------------------------------------------------------------
MOCK_RESPONSES: dict = {}


# ---------------------------------------------------------------------------
# Authentication
#
# AUTH_ENFORCE = False  →  bypass mode: credentials are logged but never rejected
# AUTH_ENFORCE = True   →  enforce mode: missing/wrong credentials return 401
#
# AUTH_SCHEMES is derived from the spec's securityDefinitions / securitySchemes.
# Edit mock_value entries to match the credentials your client will send.
# ---------------------------------------------------------------------------
AUTH_ENFORCE: bool = False

AUTH_SCHEMES: dict =    {
        "oauth2": {
            "type": "oauth2",
            "flows": {
                "clientCredentials": {
                    "tokenUrl": "https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token",
                    "scopes": {
                        "https://api.securitycenter.microsoft.com/.default": "Access Microsoft Defender for Endpoint API"
                    }
                }
            },
            "mock_value": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiAibW9jay1vYXV0aDIiLCAibW9jayI6IHRydWUsICJpc3MiOiAibW9jay1pZHAifQ.mock-sig"
        }
    }


def _validate_scheme(cfg: dict) -> bool:
    """Return True if the current request satisfies this auth scheme."""
    import base64
    t = cfg.get('type', '')
    mv = cfg.get('mock_value', '')
    http_scheme = cfg.get('scheme', '').lower()

    if t == 'apiKey':
        loc  = cfg.get('in', 'header')
        name = cfg.get('name', '')
        if loc == 'header':
            return request.headers.get(name) == mv
        if loc == 'query':
            return request.args.get(name) == mv
        if loc == 'cookie':
            return request.cookies.get(name) == mv

    if t == 'http':
        auth = request.headers.get('Authorization', '')
        if http_scheme == 'bearer':
            return auth == f'Bearer {mv}'
        if http_scheme == 'basic':
            if isinstance(mv, list) and len(mv) == 2:
                encoded = base64.b64encode(f'{mv[0]}:{mv[1]}'.encode()).decode()
            else:
                encoded = base64.b64encode(str(mv).encode()).decode()
            return auth == f'Basic {encoded}'

    if t in ('oauth2', 'openIdConnect'):
        auth = request.headers.get('Authorization', '')
        return auth == f'Bearer {mv}'

    return False


@app.before_request
def check_auth():
    """Auth gate — runs before every request."""
    if request.path.rstrip('/') in ['/mock-control', '/mock-auth-status', '/<tenant_id>/oauth2/v2.0/token']:
        return  # token endpoints and control routes are always open

    if not AUTH_SCHEMES:
        return  # spec declares no security

    # Log which credentials arrived (useful in bypass mode for debugging)
    auth_header = request.headers.get('Authorization', '<none>')
    api_key_headers = {k: v for k, v in request.headers if 'key' in k.lower() or 'token' in k.lower()}
    app.logger.debug('AUTH  path=%s  Authorization=%s  extras=%s',
                     request.path, auth_header, api_key_headers)

    if not AUTH_ENFORCE:
        return  # bypass — log only

    # Any one scheme passing is sufficient
    for cfg in AUTH_SCHEMES.values():
        if _validate_scheme(cfg):
            return

    return jsonify({
        'error': 'Unauthorized',
        'hint': 'Set AUTH_ENFORCE=False in mock_server.py to bypass, '
                'or send the correct credential from AUTH_SCHEMES.mock_value'
    }), 401


@app.route('/mock-auth-status', methods=['GET'])
def mock_auth_status():
    """Introspect current auth config — GET /mock-auth-status"""
    return jsonify({
        'AUTH_ENFORCE': AUTH_ENFORCE,
        'schemes': {
            name: {
                'type': cfg.get('type'),
                'in':   cfg.get('in'),
                'name': cfg.get('name'),
                'scheme': cfg.get('scheme'),
                'mock_value': cfg.get('mock_value'),
            }
            for name, cfg in AUTH_SCHEMES.items()
        }
    })


# ---------------------------------------------------------------------------
# Mock token endpoint(s) — simulates Step 1 of the real OAuth2 auth flow
#
# Clients POST here with client_id + client_secret + grant_type (form-encoded
# or JSON), exactly as they would against the real identity provider.
# Any client_id / client_secret is accepted — this is a mock.
#
# The returned access_token matches AUTH_SCHEMES[*].mock_value so it works
# transparently in Step 2 (API calls with Authorization: Bearer <token>).
# ---------------------------------------------------------------------------

MOCK_TOKEN_STORE: dict = {
    "oauth2":     {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiAibW9jay1vYXV0aDIiLCAibW9jayI6IHRydWUsICJpc3MiOiAibW9jay1pZHAifQ.mock-sig",
            "token_type": "Bearer",
            "expires_in": 3599,
            "scope": "https://api.securitycenter.microsoft.com/.default"
    },
}

# Token endpoint — scheme: oauth2 (clientCredentials)
# Mirrors real URL: https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token
@app.route("/<tenant_id>/oauth2/v2.0/token", methods=["POST"])
def tenant_id__oauth2_v2_0_token_endpoint(tenant_id):
    """Return a mock access token. Accepts any client_id / client_secret."""
    data = request.get_json(force=True) if request.is_json else request.form.to_dict()
    grant_type = data.get('grant_type', '')
    if grant_type != 'client_credentials':
        return jsonify({
            'error': 'unsupported_grant_type',
            'error_description': f"Expected grant_type='client_credentials', got: {grant_type}"
        }), 400
    token_data = dict(MOCK_TOKEN_STORE.get('oauth2',
                      next(iter(MOCK_TOKEN_STORE.values()))))
    app.logger.debug('TOKEN  client_id=%s  grant_type=%s',
                     data.get('client_id', '?'), grant_type)
    return jsonify(token_data), 200


# GET /api/machines — List machines
@app.route("/api/machines", methods=["GET"])
def getmachines(**kwargs):
    mock_key = 'GET:/api/machines'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "pwzdm",
        "@odata.count": 15,
        "@odata.nextLink": "qzmjh",
        "value": [
            {
                "id": "ufcha",
                "computerDnsName": "dsyex",
                "firstSeen": "2024-01-15T10:30:00Z",
                "lastSeen": "2024-01-15T10:30:00Z",
                "osPlatform": "pbaxq",
                "version": "rmdos",
                "osProcessor": "rpodr",
                "lastIpAddress": "vxcce",
                "lastExternalIpAddress": "juqqb",
                "osBuild": 30,
                "healthStatus": "Active",
                "rbacGroupId": 27,
                "rbacGroupName": "ydnvq",
                "riskScore": "None",
                "exposureLevel": "None",
                "isAadJoined": true,
                "aadDeviceId": "jaqnc",
                "machineTags": [
                    "jmean"
                ],
                "deviceValue": "Normal",
                "ipAddresses": [
                    {
                        "ipAddress": null,
                        "macAddress": null,
                        "operationalStatus": null
                    }
                ]
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /api/machines/{id}/logonusers — Get logged on users for a specific device
@app.route("/api/machines/<id>/logonusers", methods=["GET"])
def getmachinelogonusers(**kwargs):
    mock_key = 'GET:/api/machines/{id}/logonusers'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "https://api.securitycenter.microsoft.com/api/$metadata#Users",
        "@odata.count": 2,
        "value": [
            {
                "id": "CONTOSO\\\\alice.johnson",
                "accountName": "alice.johnson",
                "accountDomain": "CONTOSO",
                "accountSid": "S-1-5-21-0000000001-0000000002-0000000003-1001",
                "firstSeen": "2024-01-10T08:00:00Z",
                "lastSeen": "2024-06-01T08:15:00Z",
                "mostPrevalentMachineId": "1e5bc9d7e413ddd7902c2932e418702b84d0cc07",
                "leastPrevalentMachineId": "1e5bc9d7e413ddd7902c2932e418702b84d0cc07",
                "logonTypes": "Interactive",
                "logOnMachinesCount": 1,
                "isDomainAdmin": false,
                "isOnlyNetworkUser": false
            },
            {
                "id": "CONTOSO\\\\svc-endpoint",
                "accountName": "svc-endpoint",
                "accountDomain": "CONTOSO",
                "accountSid": "S-1-5-21-0000000001-0000000002-0000000003-2001",
                "firstSeen": "2023-01-15T10:00:00Z",
                "lastSeen": "2024-06-01T07:50:00Z",
                "mostPrevalentMachineId": "1e5bc9d7e413ddd7902c2932e418702b84d0cc07",
                "leastPrevalentMachineId": "1e5bc9d7e413ddd7902c2932e418702b84d0cc07",
                "logonTypes": "Service",
                "logOnMachinesCount": 3,
                "isDomainAdmin": false,
                "isOnlyNetworkUser": true
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /api/machines/{id}/software — Installed software inventory for a specific machine
@app.route("/api/machines/<id>/software", methods=["GET"])
def getmachinesoftware(**kwargs):
    mock_key = 'GET:/api/machines/{id}/software'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "https://api.securitycenter.microsoft.com/api/$metadata#Software",
        "@odata.count": 5,
        "value": [
            {
                "id": "microsoft-_-windows_10",
                "name": "windows_10",
                "vendor": "microsoft",
                "weaknesses": 5,
                "publicExploit": true,
                "activeAlert": false,
                "exposedMachines": 120,
                "impactScore": 7.2
            },
            {
                "id": "microsoft-_-edge",
                "name": "edge",
                "vendor": "microsoft",
                "weaknesses": 2,
                "publicExploit": false,
                "activeAlert": false,
                "exposedMachines": 45,
                "impactScore": 3.4
            },
            {
                "id": "microsoft-_-office_365",
                "name": "office_365",
                "vendor": "microsoft",
                "weaknesses": 3,
                "publicExploit": false,
                "activeAlert": false,
                "exposedMachines": 98,
                "impactScore": 4.8
            },
            {
                "id": "google-_-chrome",
                "name": "chrome",
                "vendor": "google",
                "weaknesses": 1,
                "publicExploit": false,
                "activeAlert": false,
                "exposedMachines": 88,
                "impactScore": 2.1
            },
            {
                "id": "zoom_video_communications-_-zoom",
                "name": "zoom",
                "vendor": "zoom_video_communications",
                "weaknesses": 0,
                "publicExploit": false,
                "activeAlert": false,
                "exposedMachines": 55,
                "impactScore": 0.0
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /api/machines/{id}/vulnerabilities — CVEs affecting a specific machine
@app.route("/api/machines/<id>/vulnerabilities", methods=["GET"])
def getmachinevulnerabilities(**kwargs):
    mock_key = 'GET:/api/machines/{id}/vulnerabilities'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "https://api.securitycenter.microsoft.com/api/$metadata#Vulnerabilities",
        "@odata.count": 4,
        "value": [
            {
                "id": "CVE-2024-21412",
                "name": "CVE-2024-21412",
                "description": "Internet Shortcut Files Security Feature Bypass Vulnerability allows an attacker to bypass SmartScreen.",
                "severity": "High",
                "cvssV3": 8.1,
                "exposedMachines": 34,
                "publishedOn": "2024-02-13T00:00:00Z",
                "updatedOn": "2024-03-01T00:00:00Z",
                "publicExploit": true,
                "exploitVerified": true,
                "exploitInKit": false,
                "exploitTypes": ["LocalPrivilegeEscalation"],
                "exploitUris": []
            },
            {
                "id": "CVE-2024-26234",
                "name": "CVE-2024-26234",
                "description": "Proxy Driver Spoofing Vulnerability in Windows kernel.",
                "severity": "Medium",
                "cvssV3": 6.7,
                "exposedMachines": 12,
                "publishedOn": "2024-04-09T00:00:00Z",
                "updatedOn": "2024-04-15T00:00:00Z",
                "publicExploit": false,
                "exploitVerified": false,
                "exploitInKit": false,
                "exploitTypes": [],
                "exploitUris": []
            },
            {
                "id": "CVE-2024-30051",
                "name": "CVE-2024-30051",
                "description": "Windows DWM Core Library Elevation of Privilege Vulnerability.",
                "severity": "High",
                "cvssV3": 7.8,
                "exposedMachines": 67,
                "publishedOn": "2024-05-14T00:00:00Z",
                "updatedOn": "2024-05-20T00:00:00Z",
                "publicExploit": true,
                "exploitVerified": true,
                "exploitInKit": true,
                "exploitTypes": ["LocalPrivilegeEscalation"],
                "exploitUris": []
            },
            {
                "id": "CVE-2024-29988",
                "name": "CVE-2024-29988",
                "description": "SmartScreen Prompt Security Feature Bypass Vulnerability.",
                "severity": "Critical",
                "cvssV3": 9.8,
                "exposedMachines": 8,
                "publishedOn": "2024-04-09T00:00:00Z",
                "updatedOn": "2024-04-22T00:00:00Z",
                "publicExploit": true,
                "exploitVerified": false,
                "exploitInKit": true,
                "exploitTypes": ["RemoteCodeExecution"],
                "exploitUris": []
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /api/vulnerabilities/machinesVulnerabilities — List vulnerabilities by machine and software
@app.route("/api/vulnerabilities/machinesVulnerabilities", methods=["GET"])
def getvulnerabilitiesbymachines(**kwargs):
    mock_key = 'GET:/api/vulnerabilities/machinesVulnerabilities'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "rcidq",
        "@odata.count": 37,
        "@odata.nextLink": "ljeky",
        "value": [
            {
                "id": "jmtxm",
                "cveId": "ugqnm",
                "machineId": "cgdsg",
                "fixingKbId": "olcsh",
                "productName": "htnbb",
                "productVendor": "trapd",
                "productVersion": "rgbjs",
                "severity": "Low"
            }
        ]
    }
    """)
    return jsonify(body), 200


# ---------------------------------------------------------------------------
# Runtime controls
# ---------------------------------------------------------------------------

# POST /mock-control — override any response without restarting
# Body: {"key": "GET:/users", "response": {...}, "status": 200}
@app.route("/mock-control", methods=["POST"])
def mock_control():
    data = request.get_json(force=True)
    key  = data.get('key')
    if not key:
        return jsonify({'error': 'key required'}), 400
    MOCK_RESPONSES[key] = data.get('response', {})
    MOCK_RESPONSES[key + '__status'] = data.get('status', 200)
    return jsonify({'ok': True, 'key': key}), 200


if __name__ == '__main__':
    print('Mock server for "Microsoft Defender for Endpoint API" running on http://localhost:9091')
    app.run(host='0.0.0.0', port=9091, debug=True)

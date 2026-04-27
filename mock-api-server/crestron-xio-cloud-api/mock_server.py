#!/usr/bin/env python3
"""Auto-generated mock server for: Crestron XiO Cloud API v2.0.0"""

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
        "XiOSubscriptionKey": {
            "type": "apiKey",
            "in": "header",
            "name": "XiO-subscription-key",
            "description": "API subscription key obtained from Crestron XiO Cloud portal. Requires SW-XIOC-API license.",
            "mock_value": "mock-xiosubscriptionkey-key"
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
    if request.path.rstrip('/') in ['/mock-control', '/mock-auth-status']:
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


# GET /api/v1/device/accountid/{accountid}/devices — List all devices for an account
@app.route("/api/v1/device/accountid/<accountid>/devices", methods=["GET"])
def listdevicesv1(**kwargs):
    mock_key = 'GET:/api/v1/device/accountid/{accountid}/devices'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    [
        {
            "device-cid": "1234567890abcdef",
            "device-name": "Conference Room A - TSW-1070",
            "device-model": "TSW-1070",
            "device-category": "Touch Screen",
            "device-status": "online",
            "nic-1-ip-address": "10.10.0.101",
            "nic-1-mac-address": "00.11.22.aa.bb.0",
            "serial-number": "2107ABC0001234",
            "firmware-version": "2.004.0084",
            "room-id": "room-abc123",
            "room-name": "Conference Room A",
            "last-online-datetime": "2024-06-01T14:22:00Z"
        },
        {
            "device-cid": "1234567890abcdef",
            "device-name": "Conference Room A - TSW-1070",
            "device-model": "TSW-1070",
            "device-category": "Touch Screen",
            "device-status": "online",
            "nic-1-ip-address": "10.10.1.101",
            "nic-1-mac-address": "00.11.22.aa.bb.1",
            "serial-number": "2107ABC0001234",
            "firmware-version": "2.004.0084",
            "room-id": "room-abc123",
            "room-name": "Conference Room A",
            "last-online-datetime": "2024-06-01T14:22:00Z"
        },
        {
            "device-cid": "1234567890abcdef",
            "device-name": "Conference Room A - TSW-1070",
            "device-model": "TSW-1070",
            "device-category": "Touch Screen",
            "device-status": "online",
            "nic-1-ip-address": "10.10.2.101",
            "nic-1-mac-address": "00.11.22.aa.bb.2",
            "serial-number": "2107ABC0001234",
            "firmware-version": "2.004.0084",
            "room-id": "room-abc123",
            "room-name": "Conference Room A",
            "last-online-datetime": "2024-06-01T14:22:00Z"
        },
        {
            "device-cid": "1234567890abcdef",
            "device-name": "Conference Room A - TSW-1070",
            "device-model": "TSW-1070",
            "device-category": "Touch Screen",
            "device-status": "online",
            "nic-1-ip-address": "10.10.3.101",
            "nic-1-mac-address": "00.11.22.aa.bb.3",
            "serial-number": "2107ABC0001234",
            "firmware-version": "2.004.0084",
            "room-id": "room-abc123",
            "room-name": "Conference Room A",
            "last-online-datetime": "2024-06-01T14:22:00Z"
        },
        {
            "device-cid": "1234567890abcdef",
            "device-name": "Conference Room A - TSW-1070",
            "device-model": "TSW-1070",
            "device-category": "Touch Screen",
            "device-status": "online",
            "nic-1-ip-address": "10.10.4.101",
            "nic-1-mac-address": "00.11.22.aa.bb.4",
            "serial-number": "2107ABC0001234",
            "firmware-version": "2.004.0084",
            "room-id": "room-abc123",
            "room-name": "Conference Room A",
            "last-online-datetime": "2024-06-01T14:22:00Z"
        },
        {
            "device-cid": "1234567890abcdef",
            "device-name": "Conference Room A - TSW-1070",
            "device-model": "TSW-1070",
            "device-category": "Touch Screen",
            "device-status": "online",
            "nic-1-ip-address": "10.10.5.101",
            "nic-1-mac-address": "00.11.22.aa.bb.5",
            "serial-number": "2107ABC0001234",
            "firmware-version": "2.004.0084",
            "room-id": "room-abc123",
            "room-name": "Conference Room A",
            "last-online-datetime": "2024-06-01T14:22:00Z"
        },
        {
            "device-cid": "1234567890abcdef",
            "device-name": "Conference Room A - TSW-1070",
            "device-model": "TSW-1070",
            "device-category": "Touch Screen",
            "device-status": "online",
            "nic-1-ip-address": "10.10.6.101",
            "nic-1-mac-address": "00.11.22.aa.bb.6",
            "serial-number": "2107ABC0001234",
            "firmware-version": "2.004.0084",
            "room-id": "room-abc123",
            "room-name": "Conference Room A",
            "last-online-datetime": "2024-06-01T14:22:00Z"
        },
        {
            "device-cid": "1234567890abcdef",
            "device-name": "Conference Room A - TSW-1070",
            "device-model": "TSW-1070",
            "device-category": "Touch Screen",
            "device-status": "online",
            "nic-1-ip-address": "10.10.7.101",
            "nic-1-mac-address": "00.11.22.aa.bb.7",
            "serial-number": "2107ABC0001234",
            "firmware-version": "2.004.0084",
            "room-id": "room-abc123",
            "room-name": "Conference Room A",
            "last-online-datetime": "2024-06-01T14:22:00Z"
        }
    ]
    """)
    return jsonify(body), 200


# GET /api/v1/device/accountid/{accountid}/devicecid/{devicecid}/status — Get full network status for a device (v1)
@app.route("/api/v1/device/accountid/<accountid>/devicecid/<devicecid>/status", methods=["GET"])
def getdevicestatusv1(**kwargs):
    mock_key = 'GET:/api/v1/device/accountid/{accountid}/devicecid/{devicecid}/status'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "device-cid": "1234567890abcdef",
        "device-name": "Conference Room A - TSW-1070",
        "device-model": "TSW-1070",
        "device-category": "Touch Screen",
        "device-status": "online",
        "serial-number": "2107ABC0001234",
        "firmware-version": "2.004.0084",
        "firmware-date": "2024-03-15",
        "status-host-name": "TSW-1070-CONF-A",
        "status-domain-name": "corp.example.com",
        "nic-1-ip-address": "10.10.1.101",
        "nic-1-subnet-mask": "255.255.255.0",
        "nic-1-def-router": "10.10.1.1",
        "nic-1-mac-address": "00.11.22.aa.bb.01",
        "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
        "nic-2-ip-address": "",
        "nic-2-mac-address": "",
        "last-online-datetime": "2024-06-01T14:22:00Z",
        "room-id": "room-abc123",
        "room-name": "Conference Room A"
    }
    """)
    return jsonify(body), 200


# GET /api/v2/device/accountid/{accountid}/devicecid/{devicecid}/status — Get full network status for a device (v2)
@app.route("/api/v2/device/accountid/<accountid>/devicecid/<devicecid>/status", methods=["GET"])
def getdevicestatusv2(**kwargs):
    mock_key = 'GET:/api/v2/device/accountid/{accountid}/devicecid/{devicecid}/status'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "device-cid": "1234567890abcdef",
        "device-name": "Conference Room A - TSW-1070",
        "device-model": "TSW-1070",
        "device-category": "Touch Screen",
        "device-status": "online",
        "serial-number": "2107ABC0001234",
        "firmware-version": "2.004.0084",
        "firmware-date": "2024-03-15",
        "status-host-name": "TSW-1070-CONF-A",
        "status-domain-name": "corp.example.com",
        "nic-1-ip-address": "10.10.1.101",
        "nic-1-subnet-mask": "255.255.255.0",
        "nic-1-def-router": "10.10.1.1",
        "nic-1-mac-address": "00.11.22.aa.bb.01",
        "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
        "nic-2-ip-address": "",
        "nic-2-mac-address": "",
        "last-online-datetime": "2024-06-01T14:22:00Z",
        "room-id": "room-abc123",
        "room-name": "Conference Room A"
    }
    """)
    return jsonify(body), 200


# POST /api/v2/device/accountid/{accountid}/devicestatus — Batch device status lookup
@app.route("/api/v2/device/accountid/<accountid>/devicestatus", methods=["POST"])
def batchgetdevicestatus(**kwargs):
    mock_key = 'POST:/api/v2/device/accountid/{accountid}/devicestatus'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "devices": [
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.2.0",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.bb.cc.0",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.2.1",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.bb.cc.1",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.2.2",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.bb.cc.2",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.2.3",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.bb.cc.3",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.2.4",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.bb.cc.4",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /api/v2/device/accountid/{accountId}/pageno/{pagenum}/pagesize/{pagesize}/status — List device status (paginated)
@app.route("/api/v2/device/accountid/<accountId>/pageno/<pagenum>/pagesize/<pagesize>/status", methods=["GET"])
def listdevicestatuspaginated(**kwargs):
    mock_key = 'GET:/api/v2/device/accountid/{accountId}/pageno/{pagenum}/pagesize/{pagesize}/status'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "total-count": 42,
        "page-number": 1,
        "page-size": 10,
        "devices": [
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.3.0",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.cc.dd.0",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.3.1",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.cc.dd.1",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.3.2",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.cc.dd.2",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.3.3",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.cc.dd.3",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.3.4",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.cc.dd.4",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.3.5",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.cc.dd.5",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.3.6",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.cc.dd.6",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.3.7",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.cc.dd.7",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.3.8",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.cc.dd.8",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.3.9",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.cc.dd.9",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /api/v2/device/accountid/{accountId}/devicemodel/{deviceModel}/pageno/{pagenum}/pagesize/{pagesize}/status — List device status filtered by model (paginated)
@app.route("/api/v2/device/accountid/<accountId>/devicemodel/<deviceModel>/pageno/<pagenum>/pagesize/<pagesize>/status", methods=["GET"])
def listdevicestatusbymodel(**kwargs):
    mock_key = 'GET:/api/v2/device/accountid/{accountId}/devicemodel/{deviceModel}/pageno/{pagenum}/pagesize/{pagesize}/status'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "total-count": 42,
        "page-number": 1,
        "page-size": 10,
        "devices": [
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.4.0",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.dd.ee.0",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.4.1",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.dd.ee.1",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.4.2",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.dd.ee.2",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.4.3",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.dd.ee.3",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.4.4",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.dd.ee.4",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "firmware-date": "2024-03-15",
                "status-host-name": "TSW-1070-CONF-A",
                "status-domain-name": "corp.example.com",
                "nic-1-ip-address": "10.10.4.5",
                "nic-1-subnet-mask": "255.255.255.0",
                "nic-1-def-router": "10.10.1.1",
                "nic-1-mac-address": "00.11.22.dd.ee.5",
                "nic-1-dns-servers": "10.10.1.10,10.10.1.11",
                "nic-2-ip-address": "",
                "nic-2-mac-address": "",
                "last-online-datetime": "2024-06-01T14:22:00Z",
                "room-id": "room-abc123",
                "room-name": "Conference Room A"
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /api/v1/group/accountid/{accountid}/groupid/{groupid}/devices — List devices in a group
@app.route("/api/v1/group/accountid/<accountid>/groupid/<groupid>/devices", methods=["GET"])
def listgroupdevices(**kwargs):
    mock_key = 'GET:/api/v1/group/accountid/{accountid}/groupid/{groupid}/devices'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "group-id": "grp-001",
        "group-name": "Floor 3 AV Devices",
        "devices": [
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "nic-1-ip-address": "10.10.5.0",
                "nic-1-mac-address": "00.11.22.ee.ff.0",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "room-id": "room-abc123",
                "room-name": "Conference Room A",
                "last-online-datetime": "2024-06-01T14:22:00Z"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "nic-1-ip-address": "10.10.5.1",
                "nic-1-mac-address": "00.11.22.ee.ff.1",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "room-id": "room-abc123",
                "room-name": "Conference Room A",
                "last-online-datetime": "2024-06-01T14:22:00Z"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "nic-1-ip-address": "10.10.5.2",
                "nic-1-mac-address": "00.11.22.ee.ff.2",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "room-id": "room-abc123",
                "room-name": "Conference Room A",
                "last-online-datetime": "2024-06-01T14:22:00Z"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "nic-1-ip-address": "10.10.5.3",
                "nic-1-mac-address": "00.11.22.ee.ff.3",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "room-id": "room-abc123",
                "room-name": "Conference Room A",
                "last-online-datetime": "2024-06-01T14:22:00Z"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "nic-1-ip-address": "10.10.5.4",
                "nic-1-mac-address": "00.11.22.ee.ff.4",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "room-id": "room-abc123",
                "room-name": "Conference Room A",
                "last-online-datetime": "2024-06-01T14:22:00Z"
            },
            {
                "device-cid": "1234567890abcdef",
                "device-name": "Conference Room A - TSW-1070",
                "device-model": "TSW-1070",
                "device-category": "Touch Screen",
                "device-status": "online",
                "nic-1-ip-address": "10.10.5.5",
                "nic-1-mac-address": "00.11.22.ee.ff.5",
                "serial-number": "2107ABC0001234",
                "firmware-version": "2.004.0084",
                "room-id": "room-abc123",
                "room-name": "Conference Room A",
                "last-online-datetime": "2024-06-01T14:22:00Z"
            }
        ]
    }
    """)
    return jsonify(body), 200


# POST /api/v2/deviceclaim/accountid/{accountId}/macaddress/{macaddress}/serialnumber/{serialnumber} — Claim a device by MAC address and serial number
@app.route("/api/v2/deviceclaim/accountid/<accountId>/macaddress/<macaddress>/serialnumber/<serialnumber>", methods=["POST"])
def claimdevicebymac(**kwargs):
    mock_key = 'POST:/api/v2/deviceclaim/accountid/{accountId}/macaddress/{macaddress}/serialnumber/{serialnumber}'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "device-cid": "1234567890abcdef",
        "mac-address": "00.11.22.aa.bb.cc",
        "serial-number": "2107ABC0001234",
        "claim-status": "success",
        "claimed-at": "2024-06-01T10:00:00Z"
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
    print('Mock server for "Crestron XiO Cloud API" running on http://localhost:9093')
    app.run(host='0.0.0.0', port=9093, debug=True)

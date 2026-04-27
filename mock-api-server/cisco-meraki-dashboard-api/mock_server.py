#!/usr/bin/env python3
"""Auto-generated mock server for: Cisco Meraki Dashboard API v2.0.0"""

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
AUTH_ENFORCE: bool = True

AUTH_SCHEMES: dict =    {
        "meraki_api_key": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Cisco-Meraki-API-Key",
            "mock_value": "mock-meraki-api-key-key"
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
    if request.path.rstrip('/') in ('/mock-control', '/mock-auth-status'):
        return  # always open

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


# GET /organizations — List the organizations that the user has privileges on
@app.route("/api/v1/organizations", methods=["GET"])
def getorganizations(**kwargs):
    mock_key = 'GET:/organizations'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    [
        {
            "id": "12345678901234567",
            "name": "Acme Corp",
            "url": "https://dashboard.meraki.com/o/12345678901234567/manage/organization/overview",
            "api": {
                "enabled": true
            },
            "licensing": {
                "model": "co-term"
            },
            "cloud": {
                "region": {
                    "name": "North America"
                }
            }
        },
        {
            "id": "98765432109876543",
            "name": "Globex Industries",
            "url": "https://dashboard.meraki.com/o/98765432109876543/manage/organization/overview",
            "api": {
                "enabled": true
            },
            "licensing": {
                "model": "per-device"
            },
            "cloud": {
                "region": {
                    "name": "Europe"
                }
            }
        }
    ]
    """)
    return jsonify(body), 200


# GET /organizations/{organizationId}/networks — List the networks that the user has privileges on in an organization
@app.route("/api/v1/organizations/<organizationId>/networks", methods=["GET"])
def getorganizationnetworks(**kwargs):
    mock_key = 'GET:/organizations/{organizationId}/networks'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    [
        {
            "id": "N_12345678901234567",
            "organizationId": "12345678901234567",
            "name": "Main Office",
            "productTypes": [
                "appliance",
                "switch",
                "wireless"
            ],
            "timeZone": "America/Los_Angeles",
            "tags": [
                "production"
            ],
            "enrollmentString": "enroll-abc123",
            "url": "https://dashboard.meraki.com/o/12345678901234567/manage/network/overview",
            "notes": "Headquarters network",
            "isBoundToConfigTemplate": false
        }
    ]
    """)
    return jsonify(body), 200


# GET /organizations/{organizationId}/networks/{networkId}/clients — List the clients on a network
@app.route("/api/v1/organizations/<organizationId>/networks/<networkId>/clients", methods=["GET"])
def getnetworkclients(**kwargs):
    mock_key = 'GET:/organizations/{organizationId}/networks/{networkId}/clients'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    [
        {
            "id": "k74272e",
            "mac": "00:11:22:33:44:55",
            "ip": "192.168.1.101",
            "ip6": null,
            "description": "John-MacBook-Pro",
            "firstSeen": 1704844800,
            "lastSeen": 1705104000,
            "manufacturer": "Apple",
            "os": "macOS",
            "user": "jsmith",
            "vlan": "10",
            "ssid": "Acme-Corporate",
            "switchport": null,
            "wirelessCapabilities": "802.11ac - 2.4 and 5 GHz",
            "smInstalled": false,
            "recentDeviceMac": "aa:bb:cc:dd:ee:01",
            "recentDeviceName": "AP-HQ-1F-01",
            "recentDeviceSerial": "Q2XX-XXXX-0001",
            "recentDeviceConnection": "Wireless",
            "notes": "",
            "groupPolicy8021x": null,
            "adaptivePolicyGroup": null,
            "deviceTypePrediction": "Laptop",
            "status": "Online",
            "usage": {
                "sent": 104857600,
                "recv": 524288000,
                "total": 629145600
            }
        },
        {
            "id": "m83921f",
            "mac": "66:77:88:99:aa:bb",
            "ip": "192.168.1.102",
            "ip6": "fe80::1",
            "description": "Finance-PC-01",
            "firstSeen": 1703980800,
            "lastSeen": 1705104000,
            "manufacturer": "Dell",
            "os": "Windows 11",
            "user": "agarcia",
            "vlan": "20",
            "ssid": null,
            "switchport": "GigabitEthernet1/0/5",
            "wirelessCapabilities": null,
            "smInstalled": true,
            "recentDeviceMac": "aa:bb:cc:dd:ee:02",
            "recentDeviceName": "SW-HQ-1F-01",
            "recentDeviceSerial": "Q2XX-XXXX-0002",
            "recentDeviceConnection": "Wired",
            "notes": "Finance department workstation",
            "groupPolicy8021x": "Finance-Policy",
            "adaptivePolicyGroup": null,
            "deviceTypePrediction": "Desktop",
            "status": "Online",
            "usage": {
                "sent": 52428800,
                "recv": 209715200,
                "total": 262144000
            }
        },
        {
            "id": "p91034g",
            "mac": "cc:dd:ee:ff:00:11",
            "ip": "192.168.1.150",
            "ip6": null,
            "description": "Conference-Room-TV",
            "firstSeen": 1700000000,
            "lastSeen": 1705100000,
            "manufacturer": "Samsung",
            "os": "Tizen",
            "user": null,
            "vlan": "30",
            "ssid": "Acme-IoT",
            "switchport": null,
            "wirelessCapabilities": "802.11ac - 5 GHz",
            "smInstalled": false,
            "recentDeviceMac": "aa:bb:cc:dd:ee:01",
            "recentDeviceName": "AP-HQ-1F-01",
            "recentDeviceSerial": "Q2XX-XXXX-0001",
            "recentDeviceConnection": "Wireless",
            "notes": "Conf room A display",
            "groupPolicy8021x": null,
            "adaptivePolicyGroup": null,
            "deviceTypePrediction": "Smart TV",
            "status": "Offline",
            "usage": {
                "sent": 1048576,
                "recv": 5242880,
                "total": 6291456
            }
        }
    ]
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
    print('Mock server for "Cisco Meraki Dashboard API" running on http://localhost:9090')
    app.run(host='0.0.0.0', port=9090, debug=True)

#!/usr/bin/env python3
"""Auto-generated mock server for: Verkada API v1.0.0"""

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
        "ApiKey": {
            "type": "apiKey",
            "in": "header",
            "name": "x-api-key",
            "description": "API key from Verkada Command dashboard",
            "mock_value": "mock-apikey-key"
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


# GET /cameras/v1/devices — List all cameras in the organization
@app.route("/cameras/v1/devices", methods=["GET"])
def getcameras(**kwargs):
    mock_key = 'GET:/cameras/v1/devices'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "cameras": [
            {
                "camera_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "lhhde",
                "site_id": "550e8400-e29b-41d4-a716-446655440000",
                "site_name": "amvuc",
                "model": "hkedm",
                "serial": "bhzbj",
                "mac": "lcwry",
                "local_ip": "gdive",
                "firmware": "kzcib",
                "status": "online",
                "retention_days": 47,
                "location": {
                    "latitude": 63.92,
                    "longitude": 44.52,
                    "angle": 99
                }
            }
        ],
        "next_page_token": "rdngp"
    }
    """)
    return jsonify(body), 200


# GET /cameras/v1/alerts — List camera-triggered alert events
@app.route("/cameras/v1/alerts", methods=["GET"])
def getcameraalerts(**kwargs):
    mock_key = 'GET:/cameras/v1/alerts'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "alerts": [
            {
                "alert_id": "550e8400-e29b-41d4-a716-446655440000",
                "camera_id": "550e8400-e29b-41d4-a716-446655440000",
                "camera_name": "jdkgi",
                "site_id": "550e8400-e29b-41d4-a716-446655440000",
                "created": 68,
                "notification_type": "motion",
                "objects": [
                    "person"
                ],
                "image_url": "https://example.com/resource",
                "video_url": "https://example.com/resource",
                "crowd_threshold": 66,
                "person_label": "cfpaf"
            }
        ],
        "next_page_token": "zlbgd"
    }
    """)
    return jsonify(body), 200


# GET /alarms/v1/sites — List alarm sites
@app.route("/alarms/v1/sites", methods=["GET"])
def getalarmsites(**kwargs):
    mock_key = 'GET:/alarms/v1/sites'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "sites": [
            {
                "site_id": "fc749669-1370-4a9d-84e3-daf777e0546c",
                "site_name": "HQ Building A",
                "site_security_level": "high",
                "site_state": "armed"
            },
            {
                "site_id": "fc749669-1370-4a9d-84e3-daf777e0546d",
                "site_name": "HQ Building B",
                "site_security_level": "low",
                "site_state": "disarmed"
            },
            {
                "site_id": "fc749669-1370-4a9d-84e3-daf777e0546e",
                "site_name": "Warehouse West",
                "site_security_level": "custom",
                "site_state": "armed"
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /guest/v1/sites — List guest-access sites
@app.route("/guest/v1/sites", methods=["GET"])
def getguestsites(**kwargs):
    mock_key = 'GET:/guest/v1/sites'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "sites": [
            {
                "org_id": "aaaaaaaa-bbbb-cccc-dddd-000000000001",
                "site_id": "fc749669-1370-4a9d-84e3-daf777e0546c",
                "site_name": "HQ Building A"
            },
            {
                "org_id": "aaaaaaaa-bbbb-cccc-dddd-000000000001",
                "site_id": "fc749669-1370-4a9d-84e3-daf777e0546d",
                "site_name": "HQ Building B"
            },
            {
                "org_id": "aaaaaaaa-bbbb-cccc-dddd-000000000001",
                "site_id": "fc749669-1370-4a9d-84e3-daf777e0546e",
                "site_name": "Warehouse West"
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /alarms/v1/devices — List alarm sensor devices
@app.route("/alarms/v1/devices", methods=["GET"])
def getalarmdevices(**kwargs):
    mock_key = 'GET:/alarms/v1/devices'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "alarm_devices": [
            {
                "device_id": "550e8400-e29b-41d4-a716-446655440000",
                "site_id": "550e8400-e29b-41d4-a716-446655440000",
                "site_name": "qtlhi",
                "name": "vddkj",
                "device_type": "door_contact",
                "zone": "wxfkp",
                "status": "normal",
                "camera_id": "550e8400-e29b-41d4-a716-446655440000",
                "camera_name": "iyego",
                "last_seen": 74
            }
        ],
        "next_page_token": "fxpcr"
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
    print('Mock server for "Verkada API" running on http://localhost:9092')
    app.run(host='0.0.0.0', port=9092, debug=True)

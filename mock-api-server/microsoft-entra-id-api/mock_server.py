#!/usr/bin/env python3
"""Auto-generated mock server for: Microsoft Entra ID API v1.0.0"""

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
        "EntraOAuth2": {
            "type": "oauth2",
            "flows": {
                "clientCredentials": {
                    "tokenUrl": "https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token",
                    "scopes": {
                        "https://graph.microsoft.com/.default": "Access all consented Graph permissions"
                    }
                }
            },
            "mock_value": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiAibW9jay1FbnRyYU9BdXRoMiIsICJtb2NrIjogdHJ1ZSwgImlzcyI6ICJtb2NrLWlkcCJ9.mock-sig"
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
    "EntraOAuth2":     {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiAibW9jay1FbnRyYU9BdXRoMiIsICJtb2NrIjogdHJ1ZSwgImlzcyI6ICJtb2NrLWlkcCJ9.mock-sig",
            "token_type": "Bearer",
            "expires_in": 3599,
            "scope": "https://graph.microsoft.com/.default"
    },
}

# Token endpoint — scheme: EntraOAuth2 (clientCredentials)
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
    token_data = dict(MOCK_TOKEN_STORE.get('EntraOAuth2',
                      next(iter(MOCK_TOKEN_STORE.values()))))
    app.logger.debug('TOKEN  client_id=%s  grant_type=%s',
                     data.get('client_id', '?'), grant_type)
    return jsonify(token_data), 200


# GET /v1.0/users — List all users
@app.route("/v1.0/users", methods=["GET"])
def listusers(**kwargs):
    mock_key = 'GET:/v1.0/users'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users",
        "@odata.count": 6,
        "@odata.nextLink": null,
        "value": [
            {
                "id": "aaaaaaaa-0000-0001-0000-000000000001",
                "displayName": "Alice Johnson",
                "givenName": "Alice",
                "surname": "Johnson",
                "userPrincipalName": "alice.johnson@contoso.com",
                "mail": "alice.johnson@contoso.com",
                "jobTitle": "Security Engineer",
                "department": "Information Security",
                "officeLocation": "Building A - Floor 3",
                "mobilePhone": "+1-555-0101",
                "businessPhones": [
                    "+1-555-0100"
                ],
                "accountEnabled": true,
                "userType": "Member",
                "companyName": "Contoso Ltd",
                "employeeId": "EMP-00001",
                "employeeType": "Employee",
                "securityIdentifier": "S-1-12-1-0000000001-0000000001-0000000001-0000000001",
                "onPremisesSamAccountName": "ajohnson",
                "onPremisesSyncEnabled": true,
                "onPremisesLastSyncDateTime": "2024-06-01T02:00:00Z",
                "createdDateTime": "2022-01-10T09:00:00Z",
                "preferredLanguage": "en-US"
            },
            {
                "id": "aaaaaaaa-0000-0001-0000-000000000001",
                "displayName": "Alice Johnson",
                "givenName": "Alice",
                "surname": "Johnson",
                "userPrincipalName": "alice.johnson@contoso.com",
                "mail": "alice.johnson@contoso.com",
                "jobTitle": "Security Engineer",
                "department": "Information Security",
                "officeLocation": "Building A - Floor 3",
                "mobilePhone": "+1-555-0101",
                "businessPhones": [
                    "+1-555-0100"
                ],
                "accountEnabled": true,
                "userType": "Member",
                "companyName": "Contoso Ltd",
                "employeeId": "EMP-00001",
                "employeeType": "Employee",
                "securityIdentifier": "S-1-12-1-0000000001-0000000001-0000000001-0000000001",
                "onPremisesSamAccountName": "ajohnson",
                "onPremisesSyncEnabled": true,
                "onPremisesLastSyncDateTime": "2024-06-01T02:00:00Z",
                "createdDateTime": "2022-01-10T09:00:00Z",
                "preferredLanguage": "en-US"
            },
            {
                "id": "aaaaaaaa-0000-0001-0000-000000000001",
                "displayName": "Alice Johnson",
                "givenName": "Alice",
                "surname": "Johnson",
                "userPrincipalName": "alice.johnson@contoso.com",
                "mail": "alice.johnson@contoso.com",
                "jobTitle": "Security Engineer",
                "department": "Information Security",
                "officeLocation": "Building A - Floor 3",
                "mobilePhone": "+1-555-0101",
                "businessPhones": [
                    "+1-555-0100"
                ],
                "accountEnabled": true,
                "userType": "Member",
                "companyName": "Contoso Ltd",
                "employeeId": "EMP-00001",
                "employeeType": "Employee",
                "securityIdentifier": "S-1-12-1-0000000001-0000000001-0000000001-0000000001",
                "onPremisesSamAccountName": "ajohnson",
                "onPremisesSyncEnabled": true,
                "onPremisesLastSyncDateTime": "2024-06-01T02:00:00Z",
                "createdDateTime": "2022-01-10T09:00:00Z",
                "preferredLanguage": "en-US"
            },
            {
                "id": "aaaaaaaa-0000-0001-0000-000000000001",
                "displayName": "Alice Johnson",
                "givenName": "Alice",
                "surname": "Johnson",
                "userPrincipalName": "alice.johnson@contoso.com",
                "mail": "alice.johnson@contoso.com",
                "jobTitle": "Security Engineer",
                "department": "Information Security",
                "officeLocation": "Building A - Floor 3",
                "mobilePhone": "+1-555-0101",
                "businessPhones": [
                    "+1-555-0100"
                ],
                "accountEnabled": true,
                "userType": "Member",
                "companyName": "Contoso Ltd",
                "employeeId": "EMP-00001",
                "employeeType": "Employee",
                "securityIdentifier": "S-1-12-1-0000000001-0000000001-0000000001-0000000001",
                "onPremisesSamAccountName": "ajohnson",
                "onPremisesSyncEnabled": true,
                "onPremisesLastSyncDateTime": "2024-06-01T02:00:00Z",
                "createdDateTime": "2022-01-10T09:00:00Z",
                "preferredLanguage": "en-US"
            },
            {
                "id": "aaaaaaaa-0000-0001-0000-000000000001",
                "displayName": "Alice Johnson",
                "givenName": "Alice",
                "surname": "Johnson",
                "userPrincipalName": "alice.johnson@contoso.com",
                "mail": "alice.johnson@contoso.com",
                "jobTitle": "Security Engineer",
                "department": "Information Security",
                "officeLocation": "Building A - Floor 3",
                "mobilePhone": "+1-555-0101",
                "businessPhones": [
                    "+1-555-0100"
                ],
                "accountEnabled": true,
                "userType": "Member",
                "companyName": "Contoso Ltd",
                "employeeId": "EMP-00001",
                "employeeType": "Employee",
                "securityIdentifier": "S-1-12-1-0000000001-0000000001-0000000001-0000000001",
                "onPremisesSamAccountName": "ajohnson",
                "onPremisesSyncEnabled": true,
                "onPremisesLastSyncDateTime": "2024-06-01T02:00:00Z",
                "createdDateTime": "2022-01-10T09:00:00Z",
                "preferredLanguage": "en-US"
            },
            {
                "id": "aaaaaaaa-0000-0001-0000-000000000001",
                "displayName": "Alice Johnson",
                "givenName": "Alice",
                "surname": "Johnson",
                "userPrincipalName": "alice.johnson@contoso.com",
                "mail": "alice.johnson@contoso.com",
                "jobTitle": "Security Engineer",
                "department": "Information Security",
                "officeLocation": "Building A - Floor 3",
                "mobilePhone": "+1-555-0101",
                "businessPhones": [
                    "+1-555-0100"
                ],
                "accountEnabled": true,
                "userType": "Member",
                "companyName": "Contoso Ltd",
                "employeeId": "EMP-00001",
                "employeeType": "Employee",
                "securityIdentifier": "S-1-12-1-0000000001-0000000001-0000000001-0000000001",
                "onPremisesSamAccountName": "ajohnson",
                "onPremisesSyncEnabled": true,
                "onPremisesLastSyncDateTime": "2024-06-01T02:00:00Z",
                "createdDateTime": "2022-01-10T09:00:00Z",
                "preferredLanguage": "en-US"
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /v1.0/users/{id} — Get a user by ID or UPN
@app.route("/v1.0/users/<id>", methods=["GET"])
def getuser(**kwargs):
    mock_key = 'GET:/v1.0/users/{id}'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "id": "aaaaaaaa-0000-0001-0000-000000000001",
        "displayName": "Alice Johnson",
        "givenName": "Alice",
        "surname": "Johnson",
        "userPrincipalName": "alice.johnson@contoso.com",
        "mail": "alice.johnson@contoso.com",
        "jobTitle": "Security Engineer",
        "department": "Information Security",
        "officeLocation": "Building A - Floor 3",
        "mobilePhone": "+1-555-0101",
        "businessPhones": [
            "+1-555-0100"
        ],
        "accountEnabled": true,
        "userType": "Member",
        "companyName": "Contoso Ltd",
        "employeeId": "EMP-00001",
        "employeeType": "Employee",
        "securityIdentifier": "S-1-12-1-0000000001-0000000001-0000000001-0000000001",
        "onPremisesSamAccountName": "ajohnson",
        "onPremisesSyncEnabled": true,
        "onPremisesLastSyncDateTime": "2024-06-01T02:00:00Z",
        "createdDateTime": "2022-01-10T09:00:00Z",
        "preferredLanguage": "en-US"
    }
    """)
    return jsonify(body), 200


# GET /v1.0/devices — List Entra-registered and joined devices
@app.route("/v1.0/devices", methods=["GET"])
def listdevices(**kwargs):
    mock_key = 'GET:/v1.0/devices'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users",
        "@odata.count": 8,
        "@odata.nextLink": null,
        "value": [
            {
                "id": "bbbbbbbb-0000-0001-0000-000000000001",
                "deviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "displayName": "DESKTOP-CONTOSO01",
                "accountEnabled": true,
                "operatingSystem": "Windows",
                "operatingSystemVersion": "10.0.19045.3803",
                "trustType": "AzureAd",
                "profileType": "RegisteredDevice",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "isCompliant": true,
                "isManaged": true,
                "deviceOwnership": "company",
                "managementType": "mdm",
                "enrollmentType": "windowsAzureADJoin",
                "approximateLastSignInDateTime": "2024-06-01T08:15:00Z",
                "registrationDateTime": "2023-01-15T10:00:00Z",
                "onPremisesSecurityIdentifier": "S-1-5-21-0000000001-0000000002-0000000003-1234",
                "onPremisesSyncEnabled": false,
                "physicalIds": [
                    "[ZTDID]:ZTD-CONTOSO-001",
                    "[GID]:g:00000000FFFFFFFF"
                ],
                "systemLabels": []
            },
            {
                "id": "bbbbbbbb-0000-0001-0000-000000000001",
                "deviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "displayName": "DESKTOP-CONTOSO01",
                "accountEnabled": true,
                "operatingSystem": "Windows",
                "operatingSystemVersion": "10.0.19045.3803",
                "trustType": "AzureAd",
                "profileType": "RegisteredDevice",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "isCompliant": true,
                "isManaged": true,
                "deviceOwnership": "company",
                "managementType": "mdm",
                "enrollmentType": "windowsAzureADJoin",
                "approximateLastSignInDateTime": "2024-06-01T08:15:00Z",
                "registrationDateTime": "2023-01-15T10:00:00Z",
                "onPremisesSecurityIdentifier": "S-1-5-21-0000000001-0000000002-0000000003-1234",
                "onPremisesSyncEnabled": false,
                "physicalIds": [
                    "[ZTDID]:ZTD-CONTOSO-001",
                    "[GID]:g:00000000FFFFFFFF"
                ],
                "systemLabels": []
            },
            {
                "id": "bbbbbbbb-0000-0001-0000-000000000001",
                "deviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "displayName": "DESKTOP-CONTOSO01",
                "accountEnabled": true,
                "operatingSystem": "Windows",
                "operatingSystemVersion": "10.0.19045.3803",
                "trustType": "AzureAd",
                "profileType": "RegisteredDevice",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "isCompliant": true,
                "isManaged": true,
                "deviceOwnership": "company",
                "managementType": "mdm",
                "enrollmentType": "windowsAzureADJoin",
                "approximateLastSignInDateTime": "2024-06-01T08:15:00Z",
                "registrationDateTime": "2023-01-15T10:00:00Z",
                "onPremisesSecurityIdentifier": "S-1-5-21-0000000001-0000000002-0000000003-1234",
                "onPremisesSyncEnabled": false,
                "physicalIds": [
                    "[ZTDID]:ZTD-CONTOSO-001",
                    "[GID]:g:00000000FFFFFFFF"
                ],
                "systemLabels": []
            },
            {
                "id": "bbbbbbbb-0000-0001-0000-000000000001",
                "deviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "displayName": "DESKTOP-CONTOSO01",
                "accountEnabled": true,
                "operatingSystem": "Windows",
                "operatingSystemVersion": "10.0.19045.3803",
                "trustType": "AzureAd",
                "profileType": "RegisteredDevice",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "isCompliant": true,
                "isManaged": true,
                "deviceOwnership": "company",
                "managementType": "mdm",
                "enrollmentType": "windowsAzureADJoin",
                "approximateLastSignInDateTime": "2024-06-01T08:15:00Z",
                "registrationDateTime": "2023-01-15T10:00:00Z",
                "onPremisesSecurityIdentifier": "S-1-5-21-0000000001-0000000002-0000000003-1234",
                "onPremisesSyncEnabled": false,
                "physicalIds": [
                    "[ZTDID]:ZTD-CONTOSO-001",
                    "[GID]:g:00000000FFFFFFFF"
                ],
                "systemLabels": []
            },
            {
                "id": "bbbbbbbb-0000-0001-0000-000000000001",
                "deviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "displayName": "DESKTOP-CONTOSO01",
                "accountEnabled": true,
                "operatingSystem": "Windows",
                "operatingSystemVersion": "10.0.19045.3803",
                "trustType": "AzureAd",
                "profileType": "RegisteredDevice",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "isCompliant": true,
                "isManaged": true,
                "deviceOwnership": "company",
                "managementType": "mdm",
                "enrollmentType": "windowsAzureADJoin",
                "approximateLastSignInDateTime": "2024-06-01T08:15:00Z",
                "registrationDateTime": "2023-01-15T10:00:00Z",
                "onPremisesSecurityIdentifier": "S-1-5-21-0000000001-0000000002-0000000003-1234",
                "onPremisesSyncEnabled": false,
                "physicalIds": [
                    "[ZTDID]:ZTD-CONTOSO-001",
                    "[GID]:g:00000000FFFFFFFF"
                ],
                "systemLabels": []
            },
            {
                "id": "bbbbbbbb-0000-0001-0000-000000000001",
                "deviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "displayName": "DESKTOP-CONTOSO01",
                "accountEnabled": true,
                "operatingSystem": "Windows",
                "operatingSystemVersion": "10.0.19045.3803",
                "trustType": "AzureAd",
                "profileType": "RegisteredDevice",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "isCompliant": true,
                "isManaged": true,
                "deviceOwnership": "company",
                "managementType": "mdm",
                "enrollmentType": "windowsAzureADJoin",
                "approximateLastSignInDateTime": "2024-06-01T08:15:00Z",
                "registrationDateTime": "2023-01-15T10:00:00Z",
                "onPremisesSecurityIdentifier": "S-1-5-21-0000000001-0000000002-0000000003-1234",
                "onPremisesSyncEnabled": false,
                "physicalIds": [
                    "[ZTDID]:ZTD-CONTOSO-001",
                    "[GID]:g:00000000FFFFFFFF"
                ],
                "systemLabels": []
            },
            {
                "id": "bbbbbbbb-0000-0001-0000-000000000001",
                "deviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "displayName": "DESKTOP-CONTOSO01",
                "accountEnabled": true,
                "operatingSystem": "Windows",
                "operatingSystemVersion": "10.0.19045.3803",
                "trustType": "AzureAd",
                "profileType": "RegisteredDevice",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "isCompliant": true,
                "isManaged": true,
                "deviceOwnership": "company",
                "managementType": "mdm",
                "enrollmentType": "windowsAzureADJoin",
                "approximateLastSignInDateTime": "2024-06-01T08:15:00Z",
                "registrationDateTime": "2023-01-15T10:00:00Z",
                "onPremisesSecurityIdentifier": "S-1-5-21-0000000001-0000000002-0000000003-1234",
                "onPremisesSyncEnabled": false,
                "physicalIds": [
                    "[ZTDID]:ZTD-CONTOSO-001",
                    "[GID]:g:00000000FFFFFFFF"
                ],
                "systemLabels": []
            },
            {
                "id": "bbbbbbbb-0000-0001-0000-000000000001",
                "deviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "displayName": "DESKTOP-CONTOSO01",
                "accountEnabled": true,
                "operatingSystem": "Windows",
                "operatingSystemVersion": "10.0.19045.3803",
                "trustType": "AzureAd",
                "profileType": "RegisteredDevice",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "isCompliant": true,
                "isManaged": true,
                "deviceOwnership": "company",
                "managementType": "mdm",
                "enrollmentType": "windowsAzureADJoin",
                "approximateLastSignInDateTime": "2024-06-01T08:15:00Z",
                "registrationDateTime": "2023-01-15T10:00:00Z",
                "onPremisesSecurityIdentifier": "S-1-5-21-0000000001-0000000002-0000000003-1234",
                "onPremisesSyncEnabled": false,
                "physicalIds": [
                    "[ZTDID]:ZTD-CONTOSO-001",
                    "[GID]:g:00000000FFFFFFFF"
                ],
                "systemLabels": []
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /v1.0/groups — List all groups
@app.route("/v1.0/groups", methods=["GET"])
def listgroups(**kwargs):
    mock_key = 'GET:/v1.0/groups'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users",
        "@odata.count": 5,
        "@odata.nextLink": null,
        "value": [
            {
                "id": "cccccccc-0000-0001-0000-000000000001",
                "displayName": "IT Security Team",
                "description": "All members of the Information Security department",
                "mail": "it-security@contoso.com",
                "mailEnabled": true,
                "mailNickname": "it-security",
                "securityEnabled": true,
                "securityIdentifier": "S-1-12-1-0000000002-0000000002-0000000002-0000000002",
                "groupTypes": [],
                "membershipRule": "(device.operatingSystem -eq \\"Windows\\") -and (device.deviceOwnership -eq \\"company\\")",
                "membershipRuleProcessingState": "On",
                "onPremisesSamAccountName": "IT-Security",
                "onPremisesNetBiosName": "CONTOSO",
                "onPremisesSyncEnabled": true,
                "onPremisesLastSyncDateTime": "2024-06-01T02:00:00Z",
                "isAssignableToRole": false,
                "visibility": "Private",
                "createdDateTime": "2021-03-01T12:00:00Z"
            },
            {
                "id": "cccccccc-0000-0001-0000-000000000001",
                "displayName": "IT Security Team",
                "description": "All members of the Information Security department",
                "mail": "it-security@contoso.com",
                "mailEnabled": true,
                "mailNickname": "it-security",
                "securityEnabled": true,
                "securityIdentifier": "S-1-12-1-0000000002-0000000002-0000000002-0000000002",
                "groupTypes": [],
                "membershipRule": "(device.operatingSystem -eq \\"Windows\\") -and (device.deviceOwnership -eq \\"company\\")",
                "membershipRuleProcessingState": "On",
                "onPremisesSamAccountName": "IT-Security",
                "onPremisesNetBiosName": "CONTOSO",
                "onPremisesSyncEnabled": true,
                "onPremisesLastSyncDateTime": "2024-06-01T02:00:00Z",
                "isAssignableToRole": false,
                "visibility": "Private",
                "createdDateTime": "2021-03-01T12:00:00Z"
            },
            {
                "id": "cccccccc-0000-0001-0000-000000000001",
                "displayName": "IT Security Team",
                "description": "All members of the Information Security department",
                "mail": "it-security@contoso.com",
                "mailEnabled": true,
                "mailNickname": "it-security",
                "securityEnabled": true,
                "securityIdentifier": "S-1-12-1-0000000002-0000000002-0000000002-0000000002",
                "groupTypes": [],
                "membershipRule": "(device.operatingSystem -eq \\"Windows\\") -and (device.deviceOwnership -eq \\"company\\")",
                "membershipRuleProcessingState": "On",
                "onPremisesSamAccountName": "IT-Security",
                "onPremisesNetBiosName": "CONTOSO",
                "onPremisesSyncEnabled": true,
                "onPremisesLastSyncDateTime": "2024-06-01T02:00:00Z",
                "isAssignableToRole": false,
                "visibility": "Private",
                "createdDateTime": "2021-03-01T12:00:00Z"
            },
            {
                "id": "cccccccc-0000-0001-0000-000000000001",
                "displayName": "IT Security Team",
                "description": "All members of the Information Security department",
                "mail": "it-security@contoso.com",
                "mailEnabled": true,
                "mailNickname": "it-security",
                "securityEnabled": true,
                "securityIdentifier": "S-1-12-1-0000000002-0000000002-0000000002-0000000002",
                "groupTypes": [],
                "membershipRule": "(device.operatingSystem -eq \\"Windows\\") -and (device.deviceOwnership -eq \\"company\\")",
                "membershipRuleProcessingState": "On",
                "onPremisesSamAccountName": "IT-Security",
                "onPremisesNetBiosName": "CONTOSO",
                "onPremisesSyncEnabled": true,
                "onPremisesLastSyncDateTime": "2024-06-01T02:00:00Z",
                "isAssignableToRole": false,
                "visibility": "Private",
                "createdDateTime": "2021-03-01T12:00:00Z"
            },
            {
                "id": "cccccccc-0000-0001-0000-000000000001",
                "displayName": "IT Security Team",
                "description": "All members of the Information Security department",
                "mail": "it-security@contoso.com",
                "mailEnabled": true,
                "mailNickname": "it-security",
                "securityEnabled": true,
                "securityIdentifier": "S-1-12-1-0000000002-0000000002-0000000002-0000000002",
                "groupTypes": [],
                "membershipRule": "(device.operatingSystem -eq \\"Windows\\") -and (device.deviceOwnership -eq \\"company\\")",
                "membershipRuleProcessingState": "On",
                "onPremisesSamAccountName": "IT-Security",
                "onPremisesNetBiosName": "CONTOSO",
                "onPremisesSyncEnabled": true,
                "onPremisesLastSyncDateTime": "2024-06-01T02:00:00Z",
                "isAssignableToRole": false,
                "visibility": "Private",
                "createdDateTime": "2021-03-01T12:00:00Z"
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /v1.0/servicePrincipals — List service principals
@app.route("/v1.0/servicePrincipals", methods=["GET"])
def listserviceprincipals(**kwargs):
    mock_key = 'GET:/v1.0/servicePrincipals'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users",
        "@odata.count": 5,
        "@odata.nextLink": null,
        "value": [
            {
                "id": "dddddddd-0000-0001-0000-000000000001",
                "appId": "11111111-2222-3333-4444-555555555501",
                "displayName": "Contoso Security Scanner",
                "accountEnabled": true,
                "servicePrincipalType": "Application",
                "signInAudience": "AzureADMyOrg",
                "appOwnerOrganizationId": "ffffffff-0000-0000-0000-000000000001",
                "appDisplayName": "Contoso Security Scanner",
                "description": "Internal security scanning service",
                "tags": [
                    "WindowsAzureActiveDirectoryIntegratedApp"
                ],
                "alternativeNames": [],
                "appRoleAssignmentRequired": false,
                "servicePrincipalNames": [
                    "api://contoso-security-scanner",
                    "11111111-2222-3333-4444-555555555501"
                ],
                "replyUrls": [
                    "https://contoso.com/auth/callback"
                ],
                "notificationEmailAddresses": [
                    "it-ops@contoso.com"
                ],
                "createdDateTime": "2022-06-15T09:00:00Z"
            },
            {
                "id": "dddddddd-0000-0001-0000-000000000001",
                "appId": "11111111-2222-3333-4444-555555555501",
                "displayName": "Contoso Security Scanner",
                "accountEnabled": true,
                "servicePrincipalType": "Application",
                "signInAudience": "AzureADMyOrg",
                "appOwnerOrganizationId": "ffffffff-0000-0000-0000-000000000001",
                "appDisplayName": "Contoso Security Scanner",
                "description": "Internal security scanning service",
                "tags": [
                    "WindowsAzureActiveDirectoryIntegratedApp"
                ],
                "alternativeNames": [],
                "appRoleAssignmentRequired": false,
                "servicePrincipalNames": [
                    "api://contoso-security-scanner",
                    "11111111-2222-3333-4444-555555555501"
                ],
                "replyUrls": [
                    "https://contoso.com/auth/callback"
                ],
                "notificationEmailAddresses": [
                    "it-ops@contoso.com"
                ],
                "createdDateTime": "2022-06-15T09:00:00Z"
            },
            {
                "id": "dddddddd-0000-0001-0000-000000000001",
                "appId": "11111111-2222-3333-4444-555555555501",
                "displayName": "Contoso Security Scanner",
                "accountEnabled": true,
                "servicePrincipalType": "Application",
                "signInAudience": "AzureADMyOrg",
                "appOwnerOrganizationId": "ffffffff-0000-0000-0000-000000000001",
                "appDisplayName": "Contoso Security Scanner",
                "description": "Internal security scanning service",
                "tags": [
                    "WindowsAzureActiveDirectoryIntegratedApp"
                ],
                "alternativeNames": [],
                "appRoleAssignmentRequired": false,
                "servicePrincipalNames": [
                    "api://contoso-security-scanner",
                    "11111111-2222-3333-4444-555555555501"
                ],
                "replyUrls": [
                    "https://contoso.com/auth/callback"
                ],
                "notificationEmailAddresses": [
                    "it-ops@contoso.com"
                ],
                "createdDateTime": "2022-06-15T09:00:00Z"
            },
            {
                "id": "dddddddd-0000-0001-0000-000000000001",
                "appId": "11111111-2222-3333-4444-555555555501",
                "displayName": "Contoso Security Scanner",
                "accountEnabled": true,
                "servicePrincipalType": "Application",
                "signInAudience": "AzureADMyOrg",
                "appOwnerOrganizationId": "ffffffff-0000-0000-0000-000000000001",
                "appDisplayName": "Contoso Security Scanner",
                "description": "Internal security scanning service",
                "tags": [
                    "WindowsAzureActiveDirectoryIntegratedApp"
                ],
                "alternativeNames": [],
                "appRoleAssignmentRequired": false,
                "servicePrincipalNames": [
                    "api://contoso-security-scanner",
                    "11111111-2222-3333-4444-555555555501"
                ],
                "replyUrls": [
                    "https://contoso.com/auth/callback"
                ],
                "notificationEmailAddresses": [
                    "it-ops@contoso.com"
                ],
                "createdDateTime": "2022-06-15T09:00:00Z"
            },
            {
                "id": "dddddddd-0000-0001-0000-000000000001",
                "appId": "11111111-2222-3333-4444-555555555501",
                "displayName": "Contoso Security Scanner",
                "accountEnabled": true,
                "servicePrincipalType": "Application",
                "signInAudience": "AzureADMyOrg",
                "appOwnerOrganizationId": "ffffffff-0000-0000-0000-000000000001",
                "appDisplayName": "Contoso Security Scanner",
                "description": "Internal security scanning service",
                "tags": [
                    "WindowsAzureActiveDirectoryIntegratedApp"
                ],
                "alternativeNames": [],
                "appRoleAssignmentRequired": false,
                "servicePrincipalNames": [
                    "api://contoso-security-scanner",
                    "11111111-2222-3333-4444-555555555501"
                ],
                "replyUrls": [
                    "https://contoso.com/auth/callback"
                ],
                "notificationEmailAddresses": [
                    "it-ops@contoso.com"
                ],
                "createdDateTime": "2022-06-15T09:00:00Z"
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /v1.0/users/{id}/memberOf — Groups and directory roles a user belongs to
@app.route("/v1.0/users/<id>/memberOf", methods=["GET"])
def getusermemberof(**kwargs):
    mock_key = 'GET:/v1.0/users/{id}/memberOf'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#directoryObjects",
        "@odata.count": 3,
        "value": [
            {
                "@odata.type": "#microsoft.graph.group",
                "id": "cccccccc-0000-0001-0000-000000000001",
                "displayName": "IT Security Team",
                "description": "All members of the Information Security department",
                "securityEnabled": true,
                "mailEnabled": true,
                "mailNickname": "it-security",
                "groupTypes": [],
                "onPremisesSamAccountName": "IT-Security",
                "onPremisesSyncEnabled": true
            },
            {
                "@odata.type": "#microsoft.graph.group",
                "id": "cccccccc-0000-0002-0000-000000000002",
                "displayName": "All Company Windows Devices",
                "description": "Dynamic group — all company-owned Windows devices",
                "securityEnabled": true,
                "mailEnabled": false,
                "mailNickname": "all-windows-devices",
                "groupTypes": ["DynamicMembership"],
                "membershipRule": "(device.operatingSystem -eq \\"Windows\\") -and (device.deviceOwnership -eq \\"company\\")",
                "membershipRuleProcessingState": "On"
            },
            {
                "@odata.type": "#microsoft.graph.directoryRole",
                "id": "rrrrrrrr-0000-0001-0000-000000000001",
                "displayName": "Security Reader",
                "description": "Can read security information and reports in Microsoft Entra ID and Office 365.",
                "roleTemplateId": "5d6b6bb7-de71-4623-b4af-96380a352509"
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /v1.0/groups/{id}/members — Members of a group (users and devices)
@app.route("/v1.0/groups/<id>/members", methods=["GET"])
def getgroupmembers(**kwargs):
    mock_key = 'GET:/v1.0/groups/{id}/members'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#directoryObjects",
        "@odata.count": 3,
        "value": [
            {
                "@odata.type": "#microsoft.graph.user",
                "id": "aaaaaaaa-0000-0001-0000-000000000001",
                "displayName": "Alice Johnson",
                "userPrincipalName": "alice.johnson@contoso.com",
                "mail": "alice.johnson@contoso.com",
                "jobTitle": "Security Engineer",
                "accountEnabled": true,
                "userType": "Member"
            },
            {
                "@odata.type": "#microsoft.graph.user",
                "id": "aaaaaaaa-0000-0002-0000-000000000002",
                "displayName": "Bob Martinez",
                "userPrincipalName": "bob.martinez@contoso.com",
                "mail": "bob.martinez@contoso.com",
                "jobTitle": "IT Administrator",
                "accountEnabled": true,
                "userType": "Member"
            },
            {
                "@odata.type": "#microsoft.graph.device",
                "id": "bbbbbbbb-0000-0001-0000-000000000001",
                "deviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "displayName": "DESKTOP-CONTOSO01",
                "operatingSystem": "Windows",
                "operatingSystemVersion": "10.0.19045.3803",
                "trustType": "AzureAd",
                "isCompliant": true,
                "isManaged": true
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /v1.0/devices/{id}/registeredUsers — Users registered to a device
@app.route("/v1.0/devices/<id>/registeredUsers", methods=["GET"])
def getdeviceregisteredusers(**kwargs):
    mock_key = 'GET:/v1.0/devices/{id}/registeredUsers'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#directoryObjects",
        "value": [
            {
                "@odata.type": "#microsoft.graph.user",
                "id": "aaaaaaaa-0000-0001-0000-000000000001",
                "displayName": "Alice Johnson",
                "userPrincipalName": "alice.johnson@contoso.com",
                "mail": "alice.johnson@contoso.com",
                "givenName": "Alice",
                "surname": "Johnson",
                "jobTitle": "Security Engineer",
                "department": "Information Security",
                "accountEnabled": true,
                "userType": "Member",
                "onPremisesSamAccountName": "ajohnson"
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
    print('Mock server for "Microsoft Entra ID API" running on http://localhost:9094')
    app.run(host='0.0.0.0', port=9094, debug=True)

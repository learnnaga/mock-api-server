#!/usr/bin/env python3
"""Auto-generated mock server for: Microsoft Intune API v1.0.0"""

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
        "IntuneOAuth2": {
            "type": "oauth2",
            "flows": {
                "clientCredentials": {
                    "tokenUrl": "https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token",
                    "scopes": {
                        "https://graph.microsoft.com/.default": "Access all consented Graph permissions including DeviceManagementManagedDevices.Read.All"
                    }
                }
            },
            "mock_value": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiAibW9jay1JbnR1bmVPQXV0aDIiLCAibW9jayI6IHRydWUsICJpc3MiOiAibW9jay1pZHAifQ.mock-sig"
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
    "IntuneOAuth2":     {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiAibW9jay1JbnR1bmVPQXV0aDIiLCAibW9jayI6IHRydWUsICJpc3MiOiAibW9jay1pZHAifQ.mock-sig",
            "token_type": "Bearer",
            "expires_in": 3599,
            "scope": "https://graph.microsoft.com/.default"
    },
}

# Token endpoint — scheme: IntuneOAuth2 (clientCredentials)
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
    token_data = dict(MOCK_TOKEN_STORE.get('IntuneOAuth2',
                      next(iter(MOCK_TOKEN_STORE.values()))))
    app.logger.debug('TOKEN  client_id=%s  grant_type=%s',
                     data.get('client_id', '?'), grant_type)
    return jsonify(token_data), 200


# GET /v1.0/deviceManagement/managedDevices — List all Intune-enrolled devices
@app.route("/v1.0/deviceManagement/managedDevices", methods=["GET"])
def listmanageddevices(**kwargs):
    mock_key = 'GET:/v1.0/deviceManagement/managedDevices'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "xvhkd",
        "@odata.count": 8,
        "@odata.nextLink": "qpeme",
        "value": [
            {
                "id": "eeeeeeee-0001-0001-0001-000000000001",
                "azureADDeviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "deviceName": "DESKTOP-CONTOSO01",
                "operatingSystem": "Windows",
                "osVersion": "10.0.19045.3803",
                "osBuildNumber": "19045.3803",
                "complianceState": "compliant",
                "managementAgent": "mdm",
                "managedDeviceOwnerType": "company",
                "deviceEnrollmentType": "windowsAzureADJoin",
                "joinType": "azureADJoined",
                "enrolledDateTime": "2023-01-15T10:00:00Z",
                "lastSyncDateTime": "2024-06-01T07:50:00Z",
                "emailAddress": "alice.johnson@contoso.com",
                "userDisplayName": "Alice Johnson",
                "userId": "aaaaaaaa-0000-0001-0000-000000000001",
                "userPrincipalName": "alice.johnson@contoso.com",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "serialNumber": "CNTO5540001",
                "imei": null,
                "meid": null,
                "ipAddressV4": "10.10.1.101",
                "subnetAddress": "10.10.1.0",
                "ethernetMacAddress": "00:1A:2B:3C:4D:01",
                "wiFiMacAddress": "00:1A:2B:3C:4D:A1",
                "totalStorageSpaceInBytes": 512110190592,
                "freeStorageSpaceInBytes": 214748364800,
                "physicalMemoryInBytes": 17179869184,
                "isEncrypted": true,
                "isSupervised": false,
                "jailBroken": "False",
                "azureADRegistered": true,
                "activationLockBypassCode": null,
                "remoteAssistanceSessionUrl": null,
                "hardwareInformation": {
                    "serialNumber": "CNTO5540001",
                    "totalStorageSpace": 512110190592,
                    "freeStorageSpace": 214748364800,
                    "imei": null,
                    "meid": null,
                    "manufacturer": "Dell Inc.",
                    "model": "Latitude 5540",
                    "phoneNumber": null,
                    "subscriberCarrier": null,
                    "cellularTechnology": null,
                    "wifiMac": "00:1A:2B:3C:4D:A1",
                    "operatingSystemLanguage": "en-US",
                    "isSupervised": false,
                    "isEncrypted": true,
                    "batterySerialNumber": null,
                    "batteryHealthPercentage": null,
                    "tpmSpecificationVersion": "2.0",
                    "operatingSystemEdition": "Professional",
                    "deviceFullQualifiedDomainName": "DESKTOP-CONTOSO01.corp.contoso.com",
                    "deviceGuardVirtualizationBasedSecurityHardwareRequirementState": "meetsRequirements",
                    "deviceGuardSecureBootState": "enabled"
                },
                "deviceActionResults": [
                    {
                        "actionName": null,
                        "actionState": null,
                        "startDateTime": null,
                        "lastUpdatedDateTime": null
                    }
                ]
            },
            {
                "id": "eeeeeeee-0001-0001-0001-000000000001",
                "azureADDeviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "deviceName": "DESKTOP-CONTOSO01",
                "operatingSystem": "Windows",
                "osVersion": "10.0.19045.3803",
                "osBuildNumber": "19045.3803",
                "complianceState": "compliant",
                "managementAgent": "mdm",
                "managedDeviceOwnerType": "company",
                "deviceEnrollmentType": "windowsAzureADJoin",
                "joinType": "azureADJoined",
                "enrolledDateTime": "2023-01-15T10:00:00Z",
                "lastSyncDateTime": "2024-06-01T07:50:00Z",
                "emailAddress": "alice.johnson@contoso.com",
                "userDisplayName": "Alice Johnson",
                "userId": "aaaaaaaa-0000-0001-0000-000000000001",
                "userPrincipalName": "alice.johnson@contoso.com",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "serialNumber": "CNTO5540001",
                "imei": null,
                "meid": null,
                "ipAddressV4": "10.10.1.101",
                "subnetAddress": "10.10.1.0",
                "ethernetMacAddress": "00:1A:2B:3C:4D:01",
                "wiFiMacAddress": "00:1A:2B:3C:4D:A1",
                "totalStorageSpaceInBytes": 512110190592,
                "freeStorageSpaceInBytes": 214748364800,
                "physicalMemoryInBytes": 17179869184,
                "isEncrypted": true,
                "isSupervised": false,
                "jailBroken": "False",
                "azureADRegistered": true,
                "activationLockBypassCode": null,
                "remoteAssistanceSessionUrl": null,
                "hardwareInformation": {
                    "serialNumber": "CNTO5540001",
                    "totalStorageSpace": 512110190592,
                    "freeStorageSpace": 214748364800,
                    "imei": null,
                    "meid": null,
                    "manufacturer": "Dell Inc.",
                    "model": "Latitude 5540",
                    "phoneNumber": null,
                    "subscriberCarrier": null,
                    "cellularTechnology": null,
                    "wifiMac": "00:1A:2B:3C:4D:A1",
                    "operatingSystemLanguage": "en-US",
                    "isSupervised": false,
                    "isEncrypted": true,
                    "batterySerialNumber": null,
                    "batteryHealthPercentage": null,
                    "tpmSpecificationVersion": "2.0",
                    "operatingSystemEdition": "Professional",
                    "deviceFullQualifiedDomainName": "DESKTOP-CONTOSO01.corp.contoso.com",
                    "deviceGuardVirtualizationBasedSecurityHardwareRequirementState": "meetsRequirements",
                    "deviceGuardSecureBootState": "enabled"
                },
                "deviceActionResults": [
                    {
                        "actionName": null,
                        "actionState": null,
                        "startDateTime": null,
                        "lastUpdatedDateTime": null
                    }
                ]
            },
            {
                "id": "eeeeeeee-0001-0001-0001-000000000001",
                "azureADDeviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "deviceName": "DESKTOP-CONTOSO01",
                "operatingSystem": "Windows",
                "osVersion": "10.0.19045.3803",
                "osBuildNumber": "19045.3803",
                "complianceState": "compliant",
                "managementAgent": "mdm",
                "managedDeviceOwnerType": "company",
                "deviceEnrollmentType": "windowsAzureADJoin",
                "joinType": "azureADJoined",
                "enrolledDateTime": "2023-01-15T10:00:00Z",
                "lastSyncDateTime": "2024-06-01T07:50:00Z",
                "emailAddress": "alice.johnson@contoso.com",
                "userDisplayName": "Alice Johnson",
                "userId": "aaaaaaaa-0000-0001-0000-000000000001",
                "userPrincipalName": "alice.johnson@contoso.com",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "serialNumber": "CNTO5540001",
                "imei": null,
                "meid": null,
                "ipAddressV4": "10.10.1.101",
                "subnetAddress": "10.10.1.0",
                "ethernetMacAddress": "00:1A:2B:3C:4D:01",
                "wiFiMacAddress": "00:1A:2B:3C:4D:A1",
                "totalStorageSpaceInBytes": 512110190592,
                "freeStorageSpaceInBytes": 214748364800,
                "physicalMemoryInBytes": 17179869184,
                "isEncrypted": true,
                "isSupervised": false,
                "jailBroken": "False",
                "azureADRegistered": true,
                "activationLockBypassCode": null,
                "remoteAssistanceSessionUrl": null,
                "hardwareInformation": {
                    "serialNumber": "CNTO5540001",
                    "totalStorageSpace": 512110190592,
                    "freeStorageSpace": 214748364800,
                    "imei": null,
                    "meid": null,
                    "manufacturer": "Dell Inc.",
                    "model": "Latitude 5540",
                    "phoneNumber": null,
                    "subscriberCarrier": null,
                    "cellularTechnology": null,
                    "wifiMac": "00:1A:2B:3C:4D:A1",
                    "operatingSystemLanguage": "en-US",
                    "isSupervised": false,
                    "isEncrypted": true,
                    "batterySerialNumber": null,
                    "batteryHealthPercentage": null,
                    "tpmSpecificationVersion": "2.0",
                    "operatingSystemEdition": "Professional",
                    "deviceFullQualifiedDomainName": "DESKTOP-CONTOSO01.corp.contoso.com",
                    "deviceGuardVirtualizationBasedSecurityHardwareRequirementState": "meetsRequirements",
                    "deviceGuardSecureBootState": "enabled"
                },
                "deviceActionResults": [
                    {
                        "actionName": null,
                        "actionState": null,
                        "startDateTime": null,
                        "lastUpdatedDateTime": null
                    }
                ]
            },
            {
                "id": "eeeeeeee-0001-0001-0001-000000000001",
                "azureADDeviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "deviceName": "DESKTOP-CONTOSO01",
                "operatingSystem": "Windows",
                "osVersion": "10.0.19045.3803",
                "osBuildNumber": "19045.3803",
                "complianceState": "compliant",
                "managementAgent": "mdm",
                "managedDeviceOwnerType": "company",
                "deviceEnrollmentType": "windowsAzureADJoin",
                "joinType": "azureADJoined",
                "enrolledDateTime": "2023-01-15T10:00:00Z",
                "lastSyncDateTime": "2024-06-01T07:50:00Z",
                "emailAddress": "alice.johnson@contoso.com",
                "userDisplayName": "Alice Johnson",
                "userId": "aaaaaaaa-0000-0001-0000-000000000001",
                "userPrincipalName": "alice.johnson@contoso.com",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "serialNumber": "CNTO5540001",
                "imei": null,
                "meid": null,
                "ipAddressV4": "10.10.1.101",
                "subnetAddress": "10.10.1.0",
                "ethernetMacAddress": "00:1A:2B:3C:4D:01",
                "wiFiMacAddress": "00:1A:2B:3C:4D:A1",
                "totalStorageSpaceInBytes": 512110190592,
                "freeStorageSpaceInBytes": 214748364800,
                "physicalMemoryInBytes": 17179869184,
                "isEncrypted": true,
                "isSupervised": false,
                "jailBroken": "False",
                "azureADRegistered": true,
                "activationLockBypassCode": null,
                "remoteAssistanceSessionUrl": null,
                "hardwareInformation": {
                    "serialNumber": "CNTO5540001",
                    "totalStorageSpace": 512110190592,
                    "freeStorageSpace": 214748364800,
                    "imei": null,
                    "meid": null,
                    "manufacturer": "Dell Inc.",
                    "model": "Latitude 5540",
                    "phoneNumber": null,
                    "subscriberCarrier": null,
                    "cellularTechnology": null,
                    "wifiMac": "00:1A:2B:3C:4D:A1",
                    "operatingSystemLanguage": "en-US",
                    "isSupervised": false,
                    "isEncrypted": true,
                    "batterySerialNumber": null,
                    "batteryHealthPercentage": null,
                    "tpmSpecificationVersion": "2.0",
                    "operatingSystemEdition": "Professional",
                    "deviceFullQualifiedDomainName": "DESKTOP-CONTOSO01.corp.contoso.com",
                    "deviceGuardVirtualizationBasedSecurityHardwareRequirementState": "meetsRequirements",
                    "deviceGuardSecureBootState": "enabled"
                },
                "deviceActionResults": [
                    {
                        "actionName": null,
                        "actionState": null,
                        "startDateTime": null,
                        "lastUpdatedDateTime": null
                    }
                ]
            },
            {
                "id": "eeeeeeee-0001-0001-0001-000000000001",
                "azureADDeviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "deviceName": "DESKTOP-CONTOSO01",
                "operatingSystem": "Windows",
                "osVersion": "10.0.19045.3803",
                "osBuildNumber": "19045.3803",
                "complianceState": "compliant",
                "managementAgent": "mdm",
                "managedDeviceOwnerType": "company",
                "deviceEnrollmentType": "windowsAzureADJoin",
                "joinType": "azureADJoined",
                "enrolledDateTime": "2023-01-15T10:00:00Z",
                "lastSyncDateTime": "2024-06-01T07:50:00Z",
                "emailAddress": "alice.johnson@contoso.com",
                "userDisplayName": "Alice Johnson",
                "userId": "aaaaaaaa-0000-0001-0000-000000000001",
                "userPrincipalName": "alice.johnson@contoso.com",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "serialNumber": "CNTO5540001",
                "imei": null,
                "meid": null,
                "ipAddressV4": "10.10.1.101",
                "subnetAddress": "10.10.1.0",
                "ethernetMacAddress": "00:1A:2B:3C:4D:01",
                "wiFiMacAddress": "00:1A:2B:3C:4D:A1",
                "totalStorageSpaceInBytes": 512110190592,
                "freeStorageSpaceInBytes": 214748364800,
                "physicalMemoryInBytes": 17179869184,
                "isEncrypted": true,
                "isSupervised": false,
                "jailBroken": "False",
                "azureADRegistered": true,
                "activationLockBypassCode": null,
                "remoteAssistanceSessionUrl": null,
                "hardwareInformation": {
                    "serialNumber": "CNTO5540001",
                    "totalStorageSpace": 512110190592,
                    "freeStorageSpace": 214748364800,
                    "imei": null,
                    "meid": null,
                    "manufacturer": "Dell Inc.",
                    "model": "Latitude 5540",
                    "phoneNumber": null,
                    "subscriberCarrier": null,
                    "cellularTechnology": null,
                    "wifiMac": "00:1A:2B:3C:4D:A1",
                    "operatingSystemLanguage": "en-US",
                    "isSupervised": false,
                    "isEncrypted": true,
                    "batterySerialNumber": null,
                    "batteryHealthPercentage": null,
                    "tpmSpecificationVersion": "2.0",
                    "operatingSystemEdition": "Professional",
                    "deviceFullQualifiedDomainName": "DESKTOP-CONTOSO01.corp.contoso.com",
                    "deviceGuardVirtualizationBasedSecurityHardwareRequirementState": "meetsRequirements",
                    "deviceGuardSecureBootState": "enabled"
                },
                "deviceActionResults": [
                    {
                        "actionName": null,
                        "actionState": null,
                        "startDateTime": null,
                        "lastUpdatedDateTime": null
                    }
                ]
            },
            {
                "id": "eeeeeeee-0001-0001-0001-000000000001",
                "azureADDeviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "deviceName": "DESKTOP-CONTOSO01",
                "operatingSystem": "Windows",
                "osVersion": "10.0.19045.3803",
                "osBuildNumber": "19045.3803",
                "complianceState": "compliant",
                "managementAgent": "mdm",
                "managedDeviceOwnerType": "company",
                "deviceEnrollmentType": "windowsAzureADJoin",
                "joinType": "azureADJoined",
                "enrolledDateTime": "2023-01-15T10:00:00Z",
                "lastSyncDateTime": "2024-06-01T07:50:00Z",
                "emailAddress": "alice.johnson@contoso.com",
                "userDisplayName": "Alice Johnson",
                "userId": "aaaaaaaa-0000-0001-0000-000000000001",
                "userPrincipalName": "alice.johnson@contoso.com",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "serialNumber": "CNTO5540001",
                "imei": null,
                "meid": null,
                "ipAddressV4": "10.10.1.101",
                "subnetAddress": "10.10.1.0",
                "ethernetMacAddress": "00:1A:2B:3C:4D:01",
                "wiFiMacAddress": "00:1A:2B:3C:4D:A1",
                "totalStorageSpaceInBytes": 512110190592,
                "freeStorageSpaceInBytes": 214748364800,
                "physicalMemoryInBytes": 17179869184,
                "isEncrypted": true,
                "isSupervised": false,
                "jailBroken": "False",
                "azureADRegistered": true,
                "activationLockBypassCode": null,
                "remoteAssistanceSessionUrl": null,
                "hardwareInformation": {
                    "serialNumber": "CNTO5540001",
                    "totalStorageSpace": 512110190592,
                    "freeStorageSpace": 214748364800,
                    "imei": null,
                    "meid": null,
                    "manufacturer": "Dell Inc.",
                    "model": "Latitude 5540",
                    "phoneNumber": null,
                    "subscriberCarrier": null,
                    "cellularTechnology": null,
                    "wifiMac": "00:1A:2B:3C:4D:A1",
                    "operatingSystemLanguage": "en-US",
                    "isSupervised": false,
                    "isEncrypted": true,
                    "batterySerialNumber": null,
                    "batteryHealthPercentage": null,
                    "tpmSpecificationVersion": "2.0",
                    "operatingSystemEdition": "Professional",
                    "deviceFullQualifiedDomainName": "DESKTOP-CONTOSO01.corp.contoso.com",
                    "deviceGuardVirtualizationBasedSecurityHardwareRequirementState": "meetsRequirements",
                    "deviceGuardSecureBootState": "enabled"
                },
                "deviceActionResults": [
                    {
                        "actionName": null,
                        "actionState": null,
                        "startDateTime": null,
                        "lastUpdatedDateTime": null
                    }
                ]
            },
            {
                "id": "eeeeeeee-0001-0001-0001-000000000001",
                "azureADDeviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "deviceName": "DESKTOP-CONTOSO01",
                "operatingSystem": "Windows",
                "osVersion": "10.0.19045.3803",
                "osBuildNumber": "19045.3803",
                "complianceState": "compliant",
                "managementAgent": "mdm",
                "managedDeviceOwnerType": "company",
                "deviceEnrollmentType": "windowsAzureADJoin",
                "joinType": "azureADJoined",
                "enrolledDateTime": "2023-01-15T10:00:00Z",
                "lastSyncDateTime": "2024-06-01T07:50:00Z",
                "emailAddress": "alice.johnson@contoso.com",
                "userDisplayName": "Alice Johnson",
                "userId": "aaaaaaaa-0000-0001-0000-000000000001",
                "userPrincipalName": "alice.johnson@contoso.com",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "serialNumber": "CNTO5540001",
                "imei": null,
                "meid": null,
                "ipAddressV4": "10.10.1.101",
                "subnetAddress": "10.10.1.0",
                "ethernetMacAddress": "00:1A:2B:3C:4D:01",
                "wiFiMacAddress": "00:1A:2B:3C:4D:A1",
                "totalStorageSpaceInBytes": 512110190592,
                "freeStorageSpaceInBytes": 214748364800,
                "physicalMemoryInBytes": 17179869184,
                "isEncrypted": true,
                "isSupervised": false,
                "jailBroken": "False",
                "azureADRegistered": true,
                "activationLockBypassCode": null,
                "remoteAssistanceSessionUrl": null,
                "hardwareInformation": {
                    "serialNumber": "CNTO5540001",
                    "totalStorageSpace": 512110190592,
                    "freeStorageSpace": 214748364800,
                    "imei": null,
                    "meid": null,
                    "manufacturer": "Dell Inc.",
                    "model": "Latitude 5540",
                    "phoneNumber": null,
                    "subscriberCarrier": null,
                    "cellularTechnology": null,
                    "wifiMac": "00:1A:2B:3C:4D:A1",
                    "operatingSystemLanguage": "en-US",
                    "isSupervised": false,
                    "isEncrypted": true,
                    "batterySerialNumber": null,
                    "batteryHealthPercentage": null,
                    "tpmSpecificationVersion": "2.0",
                    "operatingSystemEdition": "Professional",
                    "deviceFullQualifiedDomainName": "DESKTOP-CONTOSO01.corp.contoso.com",
                    "deviceGuardVirtualizationBasedSecurityHardwareRequirementState": "meetsRequirements",
                    "deviceGuardSecureBootState": "enabled"
                },
                "deviceActionResults": [
                    {
                        "actionName": null,
                        "actionState": null,
                        "startDateTime": null,
                        "lastUpdatedDateTime": null
                    }
                ]
            },
            {
                "id": "eeeeeeee-0001-0001-0001-000000000001",
                "azureADDeviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
                "deviceName": "DESKTOP-CONTOSO01",
                "operatingSystem": "Windows",
                "osVersion": "10.0.19045.3803",
                "osBuildNumber": "19045.3803",
                "complianceState": "compliant",
                "managementAgent": "mdm",
                "managedDeviceOwnerType": "company",
                "deviceEnrollmentType": "windowsAzureADJoin",
                "joinType": "azureADJoined",
                "enrolledDateTime": "2023-01-15T10:00:00Z",
                "lastSyncDateTime": "2024-06-01T07:50:00Z",
                "emailAddress": "alice.johnson@contoso.com",
                "userDisplayName": "Alice Johnson",
                "userId": "aaaaaaaa-0000-0001-0000-000000000001",
                "userPrincipalName": "alice.johnson@contoso.com",
                "manufacturer": "Dell Inc.",
                "model": "Latitude 5540",
                "serialNumber": "CNTO5540001",
                "imei": null,
                "meid": null,
                "ipAddressV4": "10.10.1.101",
                "subnetAddress": "10.10.1.0",
                "ethernetMacAddress": "00:1A:2B:3C:4D:01",
                "wiFiMacAddress": "00:1A:2B:3C:4D:A1",
                "totalStorageSpaceInBytes": 512110190592,
                "freeStorageSpaceInBytes": 214748364800,
                "physicalMemoryInBytes": 17179869184,
                "isEncrypted": true,
                "isSupervised": false,
                "jailBroken": "False",
                "azureADRegistered": true,
                "activationLockBypassCode": null,
                "remoteAssistanceSessionUrl": null,
                "hardwareInformation": {
                    "serialNumber": "CNTO5540001",
                    "totalStorageSpace": 512110190592,
                    "freeStorageSpace": 214748364800,
                    "imei": null,
                    "meid": null,
                    "manufacturer": "Dell Inc.",
                    "model": "Latitude 5540",
                    "phoneNumber": null,
                    "subscriberCarrier": null,
                    "cellularTechnology": null,
                    "wifiMac": "00:1A:2B:3C:4D:A1",
                    "operatingSystemLanguage": "en-US",
                    "isSupervised": false,
                    "isEncrypted": true,
                    "batterySerialNumber": null,
                    "batteryHealthPercentage": null,
                    "tpmSpecificationVersion": "2.0",
                    "operatingSystemEdition": "Professional",
                    "deviceFullQualifiedDomainName": "DESKTOP-CONTOSO01.corp.contoso.com",
                    "deviceGuardVirtualizationBasedSecurityHardwareRequirementState": "meetsRequirements",
                    "deviceGuardSecureBootState": "enabled"
                },
                "deviceActionResults": [
                    {
                        "actionName": null,
                        "actionState": null,
                        "startDateTime": null,
                        "lastUpdatedDateTime": null
                    }
                ]
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /v1.0/deviceManagement/managedDevices/{managedDeviceId} — Get a single managed device with full hardware detail
@app.route("/v1.0/deviceManagement/managedDevices/<managedDeviceId>", methods=["GET"])
def getmanageddevice(**kwargs):
    mock_key = 'GET:/v1.0/deviceManagement/managedDevices/{managedDeviceId}'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "id": "eeeeeeee-0001-0001-0001-000000000001",
        "azureADDeviceId": "eab73519-780d-4d43-be6d-a4a89af2a001",
        "deviceName": "DESKTOP-CONTOSO01",
        "operatingSystem": "Windows",
        "osVersion": "10.0.19045.3803",
        "osBuildNumber": "19045.3803",
        "complianceState": "compliant",
        "managementAgent": "mdm",
        "managedDeviceOwnerType": "company",
        "deviceEnrollmentType": "windowsAzureADJoin",
        "joinType": "azureADJoined",
        "enrolledDateTime": "2023-01-15T10:00:00Z",
        "lastSyncDateTime": "2024-06-01T07:50:00Z",
        "emailAddress": "alice.johnson@contoso.com",
        "userDisplayName": "Alice Johnson",
        "userId": "aaaaaaaa-0000-0001-0000-000000000001",
        "userPrincipalName": "alice.johnson@contoso.com",
        "manufacturer": "Dell Inc.",
        "model": "Latitude 5540",
        "serialNumber": "CNTO5540001",
        "imei": null,
        "meid": null,
        "ipAddressV4": "10.10.1.101",
        "subnetAddress": "10.10.1.0",
        "ethernetMacAddress": "00:1A:2B:3C:4D:01",
        "wiFiMacAddress": "00:1A:2B:3C:4D:A1",
        "totalStorageSpaceInBytes": 512110190592,
        "freeStorageSpaceInBytes": 214748364800,
        "physicalMemoryInBytes": 17179869184,
        "isEncrypted": true,
        "isSupervised": false,
        "jailBroken": "False",
        "azureADRegistered": true,
        "activationLockBypassCode": null,
        "remoteAssistanceSessionUrl": null,
        "hardwareInformation": {
            "serialNumber": "CNTO5540001",
            "totalStorageSpace": 512110190592,
            "freeStorageSpace": 214748364800,
            "imei": null,
            "meid": null,
            "manufacturer": "Dell Inc.",
            "model": "Latitude 5540",
            "phoneNumber": null,
            "subscriberCarrier": null,
            "cellularTechnology": null,
            "wifiMac": "00:1A:2B:3C:4D:A1",
            "operatingSystemLanguage": "en-US",
            "isSupervised": false,
            "isEncrypted": true,
            "batterySerialNumber": null,
            "batteryHealthPercentage": null,
            "tpmSpecificationVersion": "2.0",
            "operatingSystemEdition": "Professional",
            "deviceFullQualifiedDomainName": "DESKTOP-CONTOSO01.corp.contoso.com",
            "deviceGuardVirtualizationBasedSecurityHardwareRequirementState": "meetsRequirements",
            "deviceGuardSecureBootState": "enabled"
        },
        "deviceActionResults": [
            {
                "actionName": "syncDevice",
                "actionState": "done",
                "startDateTime": "2024-06-01T07:00:00Z",
                "lastUpdatedDateTime": "2024-06-01T07:01:00Z"
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /v1.0/deviceManagement/deviceCompliancePolicies — List device compliance policies
@app.route("/v1.0/deviceManagement/deviceCompliancePolicies", methods=["GET"])
def listcompliancepolicies(**kwargs):
    mock_key = 'GET:/v1.0/deviceManagement/deviceCompliancePolicies'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "aasyb",
        "@odata.count": 4,
        "@odata.nextLink": "qyhog",
        "value": [
            {
                "id": "ffffffff-0001-0001-0001-000000000001",
                "@odata.type": "#microsoft.graph.windows10CompliancePolicy",
                "displayName": "Windows 10/11 Baseline Compliance",
                "description": "Requires BitLocker, current OS build, and compliant firewall.",
                "platformType": "windows10AndLater",
                "createdDateTime": "2022-09-01T08:00:00Z",
                "lastModifiedDateTime": "2024-03-15T10:00:00Z",
                "settingsCount": 8,
                "version": 5,
                "scheduledActionsForRule": [
                    {
                        "ruleName": null,
                        "scheduledActionConfigurations": null
                    }
                ]
            },
            {
                "id": "ffffffff-0001-0001-0001-000000000001",
                "@odata.type": "#microsoft.graph.windows10CompliancePolicy",
                "displayName": "Windows 10/11 Baseline Compliance",
                "description": "Requires BitLocker, current OS build, and compliant firewall.",
                "platformType": "windows10AndLater",
                "createdDateTime": "2022-09-01T08:00:00Z",
                "lastModifiedDateTime": "2024-03-15T10:00:00Z",
                "settingsCount": 8,
                "version": 5,
                "scheduledActionsForRule": [
                    {
                        "ruleName": null,
                        "scheduledActionConfigurations": null
                    }
                ]
            },
            {
                "id": "ffffffff-0001-0001-0001-000000000001",
                "@odata.type": "#microsoft.graph.windows10CompliancePolicy",
                "displayName": "Windows 10/11 Baseline Compliance",
                "description": "Requires BitLocker, current OS build, and compliant firewall.",
                "platformType": "windows10AndLater",
                "createdDateTime": "2022-09-01T08:00:00Z",
                "lastModifiedDateTime": "2024-03-15T10:00:00Z",
                "settingsCount": 8,
                "version": 5,
                "scheduledActionsForRule": [
                    {
                        "ruleName": null,
                        "scheduledActionConfigurations": null
                    }
                ]
            },
            {
                "id": "ffffffff-0001-0001-0001-000000000001",
                "@odata.type": "#microsoft.graph.windows10CompliancePolicy",
                "displayName": "Windows 10/11 Baseline Compliance",
                "description": "Requires BitLocker, current OS build, and compliant firewall.",
                "platformType": "windows10AndLater",
                "createdDateTime": "2022-09-01T08:00:00Z",
                "lastModifiedDateTime": "2024-03-15T10:00:00Z",
                "settingsCount": 8,
                "version": 5,
                "scheduledActionsForRule": [
                    {
                        "ruleName": null,
                        "scheduledActionConfigurations": null
                    }
                ]
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /v1.0/deviceManagement/deviceConfigurations — List device configuration profiles
@app.route("/v1.0/deviceManagement/deviceConfigurations", methods=["GET"])
def listdeviceconfigurations(**kwargs):
    mock_key = 'GET:/v1.0/deviceManagement/deviceConfigurations'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "pjays",
        "@odata.count": 5,
        "@odata.nextLink": "aomwk",
        "value": [
            {
                "id": "gggggggg-0001-0001-0001-000000000001",
                "@odata.type": "#microsoft.graph.windows10GeneralConfiguration",
                "displayName": "Windows Security Baseline",
                "description": "Enforces Windows Defender, firewall rules, and UAC settings.",
                "platformApplicability": "windows10AndLater",
                "createdDateTime": "2022-10-01T09:00:00Z",
                "lastModifiedDateTime": "2024-04-01T11:00:00Z",
                "version": 3,
                "supportsScopeTags": true,
                "deviceManagementApplicabilityRuleOsEdition": {},
                "deviceManagementApplicabilityRuleOsVersion": {}
            },
            {
                "id": "gggggggg-0001-0001-0001-000000000001",
                "@odata.type": "#microsoft.graph.windows10GeneralConfiguration",
                "displayName": "Windows Security Baseline",
                "description": "Enforces Windows Defender, firewall rules, and UAC settings.",
                "platformApplicability": "windows10AndLater",
                "createdDateTime": "2022-10-01T09:00:00Z",
                "lastModifiedDateTime": "2024-04-01T11:00:00Z",
                "version": 3,
                "supportsScopeTags": true,
                "deviceManagementApplicabilityRuleOsEdition": {},
                "deviceManagementApplicabilityRuleOsVersion": {}
            },
            {
                "id": "gggggggg-0001-0001-0001-000000000001",
                "@odata.type": "#microsoft.graph.windows10GeneralConfiguration",
                "displayName": "Windows Security Baseline",
                "description": "Enforces Windows Defender, firewall rules, and UAC settings.",
                "platformApplicability": "windows10AndLater",
                "createdDateTime": "2022-10-01T09:00:00Z",
                "lastModifiedDateTime": "2024-04-01T11:00:00Z",
                "version": 3,
                "supportsScopeTags": true,
                "deviceManagementApplicabilityRuleOsEdition": {},
                "deviceManagementApplicabilityRuleOsVersion": {}
            },
            {
                "id": "gggggggg-0001-0001-0001-000000000001",
                "@odata.type": "#microsoft.graph.windows10GeneralConfiguration",
                "displayName": "Windows Security Baseline",
                "description": "Enforces Windows Defender, firewall rules, and UAC settings.",
                "platformApplicability": "windows10AndLater",
                "createdDateTime": "2022-10-01T09:00:00Z",
                "lastModifiedDateTime": "2024-04-01T11:00:00Z",
                "version": 3,
                "supportsScopeTags": true,
                "deviceManagementApplicabilityRuleOsEdition": {},
                "deviceManagementApplicabilityRuleOsVersion": {}
            },
            {
                "id": "gggggggg-0001-0001-0001-000000000001",
                "@odata.type": "#microsoft.graph.windows10GeneralConfiguration",
                "displayName": "Windows Security Baseline",
                "description": "Enforces Windows Defender, firewall rules, and UAC settings.",
                "platformApplicability": "windows10AndLater",
                "createdDateTime": "2022-10-01T09:00:00Z",
                "lastModifiedDateTime": "2024-04-01T11:00:00Z",
                "version": 3,
                "supportsScopeTags": true,
                "deviceManagementApplicabilityRuleOsEdition": {},
                "deviceManagementApplicabilityRuleOsVersion": {}
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /v1.0/deviceManagement/managedDevices/{managedDeviceId}/deviceCompliancePolicyStates — Get per-device compliance policy results
@app.route("/v1.0/deviceManagement/managedDevices/<managedDeviceId>/deviceCompliancePolicyStates", methods=["GET"])
def getdevicecompliancepolicystates(**kwargs):
    mock_key = 'GET:/v1.0/deviceManagement/managedDevices/{managedDeviceId}/deviceCompliancePolicyStates'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "xdhrk",
        "@odata.count": 13,
        "@odata.nextLink": "lsjmc",
        "value": [
            {
                "id": "ffffffff-0001-0001-0001-000000000001",
                "displayName": "Windows 10/11 Baseline Compliance",
                "version": 5,
                "platformType": "windows10AndLater",
                "state": "compliant",
                "settingCount": 8,
                "settingStates": [
                    {
                        "setting": null,
                        "settingName": null,
                        "instanceDisplayName": null,
                        "state": null,
                        "errorCode": null,
                        "errorDescription": null,
                        "sources": null
                    }
                ]
            },
            {
                "id": "ffffffff-0001-0001-0001-000000000001",
                "displayName": "Windows 10/11 Baseline Compliance",
                "version": 5,
                "platformType": "windows10AndLater",
                "state": "compliant",
                "settingCount": 8,
                "settingStates": [
                    {
                        "setting": null,
                        "settingName": null,
                        "instanceDisplayName": null,
                        "state": null,
                        "errorCode": null,
                        "errorDescription": null,
                        "sources": null
                    }
                ]
            },
            {
                "id": "ffffffff-0001-0001-0001-000000000001",
                "displayName": "Windows 10/11 Baseline Compliance",
                "version": 5,
                "platformType": "windows10AndLater",
                "state": "compliant",
                "settingCount": 8,
                "settingStates": [
                    {
                        "setting": null,
                        "settingName": null,
                        "instanceDisplayName": null,
                        "state": null,
                        "errorCode": null,
                        "errorDescription": null,
                        "sources": null
                    }
                ]
            }
        ]
    }
    """)
    return jsonify(body), 200


# GET /v1.0/deviceManagement/managedDevices/{managedDeviceId}/users — Users associated with a managed device
@app.route("/v1.0/deviceManagement/managedDevices/<managedDeviceId>/users", methods=["GET"])
def getmanageddeviceusers(**kwargs):
    mock_key = 'GET:/v1.0/deviceManagement/managedDevices/{managedDeviceId}/users'
    if mock_key in MOCK_RESPONSES:
        return jsonify(MOCK_RESPONSES[mock_key]), MOCK_RESPONSES.get(mock_key + '__status', 200)
    body = json.loads("""
    {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users",
        "value": [
            {
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
    print('Mock server for "Microsoft Intune API" running on http://localhost:9095')
    app.run(host='0.0.0.0', port=9095, debug=True)

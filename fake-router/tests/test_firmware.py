"""Tests for GET /firmware/version.

Will verify response shape and behavior under normal and fault modes.
"""

def test_get_firmware_version(client):
    response = client.get("/firmware/version")

    assert response.status_code == 200
    assert response.json() == {
        "product": "ReleaseGuard Fake Router",
        "firmware_version": "2.4.1",
        "build_id": "router-api-v1.0"
    }

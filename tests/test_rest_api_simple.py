"""Sanity checks for REST API."""
import base64


def test_resources(client):
    """Verify GET requests to initial endpoint.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Verify response with information listed in the spec.
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert response.get_json() == {
        "posts": "/api/v1/posts/",
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "url": "/api/v1/",
    }


def test_login_session(client):
    """Verify GET request to posts route with login session.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Access denied without credentials
    response = client.get("/api/v1/posts/")
    assert response.status_code == 403

    # Login
    client.post(
        "/accounts/",
        data={
            "operation": "login",
            "username": "awdeorio",
            "password": "password"
        }
    )

    # Access granted because session already exists
    response = client.get("/api/v1/posts/")
    assert response.status_code == 200


def test_http_basic_auth(client):
    """Verify GET request to posts route with HTTP Basic Auth.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Access denied without credentials
    response = client.get("/api/v1/posts/")
    assert response.status_code == 403

    # Access granted with credentials
    credentials = base64.b64encode(b"awdeorio:password").decode("utf-8")
    response = client.get(
        "/api/v1/posts/",
        headers={"Authorization": f"Basic {credentials}"},
    )
    assert response.status_code == 200

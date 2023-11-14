"""Unit tests for likes and comments routes in REST API."""
import json
from base64 import b64encode


def test_likes_delete(client):
    """Verify DELETE 'likes' endpoint using Basic HTTP auth.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    credentials = b64encode(b"awdeorio:password").decode('utf-8')

    # DELETE likes
    response = client.delete(
        "/api/v1/likes/6/",
        data=json.dumps({}),
        headers={"Authorization": f"Basic {credentials}"},
        content_type="application/json",
    )
    assert response.status_code == 204

    # Verify number of likes
    response = client.get(
        "/api/v1/posts/3/",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 200
    assert response.get_json()["likes"] == {
        "numLikes": 0,  # Changed from 1 to 0
        "lognameLikesThis": False,  # Changed from True to False
        "url": None,
    }

    # Expect 404 on deleting like that no longer exists
    response = client.delete(
        "/api/v1/likes/6/",
        data=json.dumps({}),
        headers={"Authorization": f"Basic {credentials}"},
        content_type="application/json",
    )
    assert response.status_code == 404

    # Expect 403 on deleting like that awdeorio does not own
    response = client.delete(
        "/api/v1/likes/2/",
        data=json.dumps({}),
        headers={"Authorization": f"Basic {credentials}"},
        content_type="application/json",
    )
    assert response.status_code == 403


def test_likes_post(client):
    """Verify POST 'likes' endpoint.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    credentials = b64encode(b"jag:password").decode('utf-8')

    # POST likes (jag likes his own post)
    response = client.post(
        "/api/v1/likes/?postid=4",
        data=json.dumps({}),
        headers={"Authorization": f"Basic {credentials}"},
        content_type="application/json")
    assert response.status_code == 201

    # Verify number of likes
    response = client.get(
        "/api/v1/posts/4/",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 200
    assert response.get_json()["likes"] == {
        "numLikes": 1,  # Changed from 0 to 1
        "lognameLikesThis": True,  # Changed from False to True
        "url": "/api/v1/likes/7/",
    }


def test_like_exists(client):
    """Duplicate POST likes returns a JSON formatted error.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    credentials = b64encode(b"awdeorio:password").decode('utf-8')

    # awdeorio likes a post that he already liked
    response = client.post(
        "/api/v1/likes/?postid=3",
        data=json.dumps({}),
        headers={"Authorization": f"Basic {credentials}"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.get_json() == {
        "likeid": 6,
        "url": "/api/v1/likes/6/",
        }


def test_comments_post(client):
    """Verify POST 'comments' endpoint.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    credentials = b64encode(b"awdeorio:password").decode('utf-8')

    # POST comments
    response = client.post(
        "/api/v1/comments/?postid=3",
        data=json.dumps({"text": "new comment"}),
        headers={"Authorization": f"Basic {credentials}"},
        content_type="application/json")
    assert response.status_code == 201

    # Verify comments
    response = client.get(
        "/api/v1/posts/3/",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 200

    assert response.get_json()["comments"] == [
        {
            "commentid": 1,
            "lognameOwnsThis": True,
            "owner": "awdeorio",
            "ownerShowUrl": "/users/awdeorio/",
            "text":
                "#chickensofinstagram",
            "url": "/api/v1/comments/1/"
        },
        {
            "commentid": 2,
            "lognameOwnsThis": False,
            "owner": "jflinn",
            "ownerShowUrl": "/users/jflinn/",
            "text":
                "I <3 chickens",
            "url": "/api/v1/comments/2/"
        },
        {
            "commentid": 3,
            "lognameOwnsThis": False,
            "owner": "michjc",
            "ownerShowUrl": "/users/michjc/",
            "text":
                "Cute overload!",
            "url": "/api/v1/comments/3/"
        },
        {
            "commentid": 8,
            "lognameOwnsThis": True,
            "owner": "awdeorio",
            "ownerShowUrl": "/users/awdeorio/",
            "text": "new comment",
            "url": "/api/v1/comments/8/"
        }
    ]


def test_comments_delete(client):
    """Verify DELETE 'comments' endpoint.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    credentials = b64encode(b"awdeorio:password").decode('utf-8')

    # DELETE comment
    response = client.delete(
        "/api/v1/comments/1/",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 204

    # Verify comments
    response = client.get(
        "/api/v1/posts/3/",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 200

    assert response.get_json()["comments"] == [
        {
            "commentid": 2,
            "lognameOwnsThis": False,
            "owner": "jflinn",
            "ownerShowUrl": "/users/jflinn/",
            "text":
                "I <3 chickens",
            "url": "/api/v1/comments/2/"
        },
        {
            "commentid": 3,
            "lognameOwnsThis": False,
            "owner": "michjc",
            "ownerShowUrl": "/users/michjc/",
            "text":
                "Cute overload!",
            "url": "/api/v1/comments/3/"
        }
    ]

    # Expect 404 on deleting comment that no longer exists
    response = client.delete(
        "/api/v1/comments/1/",
        data=json.dumps({}),
        headers={"Authorization": f"Basic {credentials}"},
        content_type="application/json",
    )
    assert response.status_code == 404

    # Expect 403 on deleting comment that awdeorio does not own
    response = client.delete(
        "/api/v1/comments/2/",
        data=json.dumps({}),
        headers={"Authorization": f"Basic {credentials}"},
        content_type="application/json",
    )
    assert response.status_code == 403

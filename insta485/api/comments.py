"""REST API for comments."""
import flask
import insta485
from .service_api import (requires_auth,
                          raise_forbidden, get_authenticated_db_connection)


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def post_comment():
    """Post one comment to postid."""
    # Login check
    logname = requires_auth()
    if not logname:
        return raise_forbidden()
    connection = insta485.model.get_db()

    postid = flask.request.args.get("postid")

    # postid in range check
    cur = connection.execute(
            "SELECT postid FROM posts WHERE postid = ?",
            (postid,)
    )
    print("hello, world")
    if not cur.fetchone():
        return '', 404

    # Post comment
    text = flask.request.get_json()["text"]
    print("goodbye, world")
    print(flask.request.get_json())
    if not text:
        return '', 404
    connection.execute(
            "INSERT INTO comments (owner, postid, text) "
            "VALUES (?, ?, ?) ",
            (logname, postid, text,)
    )

    # Retrieve comment information
    cur = connection.execute(
            "SELECT commentid, owner, text "
            "FROM comments WHERE commentid = last_insert_rowid()"
    )
    comment = cur.fetchone()
    comment["lognameOwnsThis"] = True
    comment["ownerShowUrl"] = f"/users/{logname}/"
    comment["url"] = flask.request.path

    return flask.jsonify(comment), 201


@insta485.app.route('/api/v1/comments/<commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    """Delete the comment by commentid."""
    logname, connection = get_authenticated_db_connection()

    cur = connection.execute(
        "SELECT owner FROM comments WHERE commentid = ?",
        (commentid, )
    )
    comment = cur.fetchone()
    if not comment:
        # comment not exist
        return '', 404
    if comment["owner"] != logname:
        # not owned by logname
        return '', 403
    # delete comment
    connection.execute(
        "DELETE FROM comments WHERE commentid = ?",
        (commentid, )
    )
    return '', 204

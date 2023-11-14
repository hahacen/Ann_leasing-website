"""REST API for likes."""
import flask
import insta485
from .service_api import requires_auth, raise_forbidden


@insta485.app.route('/api/v1/likes/<likeid>/', methods=['DELETE'])
def delete_like(likeid):
    """Delete a like by its ID."""
    # Login Check
    logname = requires_auth()
    print(logname)
    if not logname:
        return raise_forbidden()
    # Build connection
    connection = insta485.model.get_db()
    # 1. Check if the like exists
    cur = connection.execute('SELECT * FROM likes WHERE likeid = ?', (likeid,))
    like = cur.fetchone()
    if not like:
        return flask.jsonify({"message": "Like not found"}), 404
    # 2. Check if the authenticated user owns the like
    print(logname, like["owner"])
    if logname != like["owner"]:
        return flask.jsonify({"message": "Forbidden action"}), 403
    # 3. Delete the like
    connection.execute('DELETE FROM likes WHERE likeid = ?', (likeid, ))
    connection.commit()
    # return HTTP/1.0 204 NO CONTENT
    return '', 204


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def like_post():
    """Post a like."""
    logname = requires_auth()
    if not logname:
        return raise_forbidden()

    postid = flask.request.args.get('postid')
    if not postid:
        return flask.jsonify({"message": "postid required"}), 400
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM likes where postid =? and owner = ?",
        (postid, logname)
    )
    like = cur.fetchone()
    cur = connection.execute("SELECT MAX(postid) FROM posts")
    max_value = cur.fetchone()["MAX(postid)"]
    if int(postid) > max_value:
        error_message = {
              "message": "Not Found",
              "status_code": 404
            }
        return flask.jsonify(error_message), 404
    # if like already exists
    if like:
        like_object = {"likeid": like["likeid"],
                       "url": f"/api/v1/likes/{like['likeid']}/"
                       }
        return flask.jsonify(like_object), 200
    # create the like
    connection.execute(
        "INSERT INTO likes (owner, postid) VALUES (?, ?)",
        (logname, postid)
    )
    cur = connection.execute(
        "SELECT * FROM likes where postid =? and owner = ?",
        (postid, logname)
    )
    like_created = cur.fetchone()
    like_object = {
        "likeid": like_created["likeid"],
        "url": f"/api/v1/likes/{like_created['likeid']}/"
    }
    return flask.jsonify(like_object), 201

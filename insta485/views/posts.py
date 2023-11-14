"""
Insta485 posts view.

URLs include:
/posts/<postid_url_slug>/
"""

import pathlib
import uuid
import arrow
import flask
import insta485


@insta485.app.route('/posts/<postid_url_slug>/')
def show_post(postid_url_slug):
    """Display /posts/<postid_url_slug>/."""
    connection = insta485.model.get_db()

    logname = flask.session['username']
    cur = connection.execute(
        "SELECT posts.postid, posts.filename, posts.owner, posts.created, "
        "users.filename AS userfile "
        "FROM  posts, users "
        "WHERE posts.postid = ? "
        "AND users.username = posts.owner",
        (postid_url_slug, )
    )
    post = cur.fetchone()
    post["created"] = arrow.get(post["created"]).humanize()
    # fetching likes
    cur = connection.execute(
        "SELECT COUNT(*) "
        "FROM likes "
        "WHERE postid = ?",
        (postid_url_slug,)
    )
    likes_result = cur.fetchone()
    post["num_like"] = likes_result['COUNT(*)']
    cur = connection.execute(
        "SELECT * "
        "FROM likes "
        "WHERE likes.owner = ? "
        "AND likes.postid = ?",
        (logname, postid_url_slug,)
    )
    post["like_status"] = 1 if cur.fetchone() else 0
    # fetching comments
    cur = connection.execute(
        "SELECT owner, text, commentid, created "
        "FROM comments "
        "WHERE postid = ? "
        "ORDER BY created ASC",
        (postid_url_slug,)
    )
    post["comments"] = cur.fetchall()
    context = {"post": post, "logname": logname}
    return flask.render_template("post.html", **context)


@insta485.app.route('/posts/', methods=['POST'])
def post_operation():
    """Operate on deleting and creating a post."""
    logname = flask.session['username']
    connection = insta485.model.get_db()
    # If the value of ?target is not set, redirect to /users/<logname>/.
    target_url = flask.request.args.get('target', f"/users/{logname}/")
    operation = flask.request.form.get('operation')
    if operation == "create":
        # If a user tries to create a post with an empty file, then abort(400).
        if ('file' not in flask.request.files or
                flask.request.files['file'].filename == ''):
            flask.abort(400)
        # Unpack flask object
        fileobj = flask.request.files["file"]
        filename = fileobj.filename
        # name file
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"
        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"] / uuid_basename
        fileobj.save(path)
        cur = connection.execute(
            'INSERT INTO posts '
            '(filename, owner) '
            'VALUES (?, ?)', (uuid_basename, logname,)
        )
    elif operation == "delete":
        postid = flask.request.form.get('postid')
        # If a user tries to delete a post that they do not own,
        # then abort(403).
        cur = connection.execute(
            'SELECT * FROM posts '
            'WHERE owner = ? '
            'AND postid = ?',
            (logname, postid,)
        )
        post = cur.fetchone()
        if not post:
            flask.abort(403)

        filename = post['filename']
        path = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"]/filename)
        path.unlink()

        cur = connection.execute(
            'DELETE FROM posts '
            'WHERE owner = ? '
            'AND postid = ?',
            (logname, postid,)
        )
    return flask.redirect(target_url)

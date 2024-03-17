"""
Insta485 users view.

URLs include:
/users/<user_url_slug>/
/users/<user_url_slug>/followers/
"""
import flask
import insta485


@insta485.app.route('/users/<user_url_slug>/')
def show_user_page(user_url_slug):
    # TODO: modify database execution
    """Display /users/<user_url_slug>/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # Query database to get the user info
    user_info = connection.execute(
        "SELECT username, fullname, filename, created "
        "FROM users WHERE username = ?",
        (user_url_slug,)
    )

    user = user_info.fetchone()

    if not user:
        flask.abort(404)

    cur = connection.execute(
        "SELECT COUNT(*) AS post_cnt "
        "FROM posts "
        "WHERE posts.owner = ? ",
        (user_url_slug,)
    )

    user["post_cnt"] = cur.fetchone()["post_cnt"]

    cur = connection.execute(
        "SELECT COUNT(*) AS follower_cnt "
        "FROM following "
        "WHERE username2 = ?",
        (user_url_slug,)
    )

    user["follower_cnt"] = cur.fetchone()["follower_cnt"]

    cur = connection.execute(
        "SELECT COUNT(*) AS following_cnt "
        "FROM following "
        "WHERE following.username1 = ? ",
        (user_url_slug, )
    )
    user["following_cnt"] = cur.fetchone()["following_cnt"]

    cur = connection.execute(
        "SELECT postid, filename "
        "FROM posts "
        "WHERE owner = ? "
        "ORDER BY postid",
        (user_url_slug, )
    )
    user["post_path"] = cur.fetchall()

    logname = flask.session['username']

    cur = connection.execute(
        "SELECT * "
        "FROM following "
        "WHERE username1 = ? AND username2 = ?",
        (logname, user_url_slug,)
    )
    user["following_status"] = 0 if not cur.fetchone() else 1

    context = {"userinfo": user,
               "logname": logname}

    return flask.render_template("user.html", **context)


@insta485.app.route('/users/<user_url_slug>/followers/')
def show_user_followers(user_url_slug):
    """Display /users/<user_url_slug>/follower/."""
    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT username "
        "FROM users WHERE username = ?",
        (user_url_slug,)
    )

    user = cur.fetchone()

    if not user:
        flask.abort(404)

    cur = connection.execute(
        "SELECT users.username AS un, users.filename AS fn "
        "FROM users, following "
        "WHERE following.username1 = users.username "
        "AND following.username2 = ? ",
        (user_url_slug,)
    )

    follower_user = cur.fetchall()

    logname = flask.session['username']

    for one_user in follower_user:
        cur = connection.execute(
            "SELECT * "
            "FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, one_user["un"],)
        )
        one_user["follower_status"] = 0 if not cur.fetchone() else 1

    context = {"follower_user": follower_user,
               "logname": logname}

    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<user_url_slug>/following/')
def show_user_following(user_url_slug):
    """Display /users/<user_url_slug>/following/."""
    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT username "
        "FROM users WHERE username = ?",
        (user_url_slug,)
    )

    user = cur.fetchone()

    if not user:
        flask.abort(404)

    cur = connection.execute(
        "SELECT users.username AS un, users.filename AS fn "
        "FROM users, following "
        "WHERE following.username1 = ? "
        "AND following.username2 = users.username ",
        (user_url_slug,)
    )

    following_user = cur.fetchall()

    logname = flask.session['username']
    for one_user in following_user:
        cur = connection.execute(
            "SELECT * "
            "FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, one_user["un"],)
        )
        one_user["following_status"] = 0 if not cur.fetchone() else 1

    context = {"following_user": following_user,
               "logname": logname}

    return flask.render_template("following.html", **context)


@insta485.app.route('/following/', methods=['POST'])
def follower_operation():
    """Operates follow and unfollow actions."""
    logname = flask.session['username']
    connection = insta485.model.get_db()
    target_url = flask.request.args.get('target')
    operation = flask.request.form.get('operation')
    username = flask.request.form['username']
    if operation == "follow":
        cur = connection.execute(
            'SELECT * FROM '
            'following WHERE '
            'username1 = ? '
            'AND username2 = ?',
            (logname, username,)
        )
        if cur.fetchone():
            # Conflict, already following
            flask.abort(409)
        cur = connection.execute(
            'INSERT INTO following '
            '(username1, username2) '
            'VALUES (?, ?)',
            (logname, username,)
        )
    elif operation == "unfollow":
        # Conflict, not following
        cur = connection.execute(
            'SELECT * FROM following '
            'WHERE username1 = ? '
            'AND username2 = ?',
            (logname, username,)
        )
        if not cur.fetchone():
            flask.abort(409)
        cur = connection.execute(
            'DELETE FROM following WHERE '
            'username1 = ? AND username2 = ?',
            (logname, username,)
        )
    return flask.redirect(target_url)

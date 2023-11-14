"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import arrow
import insta485

from insta485.api.service_api import requires_auth


@insta485.app.route('/')
def show_index():
    """Display / route."""
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    logname = requires_auth()
    if not logname:
        return flask.redirect(flask.url_for('accounts_login'))
    cur = connection.execute(
        "SELECT username, fullname "
        "FROM users "
        "WHERE username = ?",
        (logname, )
    )
    users = cur.fetchall()
    # fetch logname's username and fullname

    cur = connection.execute(
        "SELECT DISTINCT posts.postid, "
        "posts.filename, posts.owner, posts.created, "
        "users.filename AS userfile "
        "FROM following, posts, users "
        "WHERE following.username1 = ? "
        "AND (posts.owner = following.username2 "
        "OR posts.owner = following.username1) "
        "AND posts.owner = users.username "
        "ORDER BY posts.postid DESC ",
        (logname, )
    )

    posts = cur.fetchall()

    for post in posts:
        post["created"] = arrow.get(post["created"]).humanize()
        cur = connection.execute(
            "SELECT COUNT(*) FROM "
            "likes "
            "WHERE postid = ?",
            (post["postid"],)
        )
        likes_result = cur.fetchall()
        post["num_like"] = likes_result[0]['COUNT(*)']

        cur = connection.execute(
            "SELECT * "
            "FROM likes WHERE "
            "likes.owner = ? "
            "AND likes.postid = ?",
            (logname, post["postid"],)
        )
        post["like_status"] = 1 if cur.fetchone() else 0
        # fetching comments
        cur = connection.execute(
            "SELECT owner, text, created "
            "FROM comments "
            "WHERE postid = ? "
            "ORDER BY created ASC",
            (post["postid"],)
        )
        post["comments"] = cur.fetchall()
    # Add database info to context
    context = {"users": users,
               "posts": posts,
               "logname": logname}
    return flask.render_template("index.html", **context)


# @insta485.app.route('/account/login/', methods=['GET']) #没有post method
# def login():
#     if flask.request.method == 'POST':
#         username = flask.request.form.get('username')
#         password = flask.request.form.get('password')
#         operation = flask.request.form.get('operation')

#         if operation == "login" and username.get(username) == password:
#             # Successful login
#             return flask.redirect(url_for('index'))
#         else:
#             # Failed login
#             return "Login failed!", 401
#     context = {}
#     return flask.render_template("login.html", **context)

@insta485.app.route('/uploads/<filename>')
def download_file(filename):
    """Download files from the upload folder."""
    if 'username' not in flask.session:
        flask.abort(403)
    upload_folder = insta485.app.config['UPLOAD_FOLDER']
    return flask.send_from_directory(upload_folder, filename)

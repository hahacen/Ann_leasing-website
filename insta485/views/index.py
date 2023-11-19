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
    if_login = True
    if not logname:
        # return flask.redirect(flask.url_for('accounts_login'))
        if_login = False

    cur = connection.execute(
        "SELECT username, fullname "
        "FROM users "
        "WHERE username = ?",
        (logname, )
    )
    users = cur.fetchall()
    # fetch logname's username and fullname

    cur = connection.execute(
        "SELECT posts.postid, posts.filename, posts.owner, posts.created, "
        "users.filename AS userfile "
        "FROM starred_posts "
        "JOIN posts ON starred_posts.postid = posts.postid "
        "JOIN users ON posts.owner = users.username "
        "WHERE starred_posts.username = ? "
        "ORDER BY posts.created DESC",
        (logname, )
    )
    starred_posts = cur.fetchall()

    for post in starred_posts:
        post["created"] = arrow.get(post["created"]).humanize()

        # cur = connection.execute(
        #     "SELECT * "
        #     "FROM likes WHERE "
        #     "likes.owner = ? "
        #     "AND likes.postid = ?",
        #     (logname, post["postid"],)
        # )
        # post["like_status"] = 1 if cur.fetchone() else 0
        # # fetching comments
        # cur = connection.execute(
        #     "SELECT owner, text, created "
        #     "FROM comments "
        #     "WHERE postid = ? "
        #     "ORDER BY created ASC",
        #     (post["postid"],)
        # )
        # post["comments"] = cur.fetchall()
    # Add database info to context
    context = {"users": users,
               "posts": starred_posts,
               "logname": logname,
               "if_login": if_login}
    return flask.render_template("home.html", **context)


@insta485.app.route('/uploads/<filename>')
def download_file(filename):
    """Download files from the upload folder."""
    if 'username' not in flask.session:
        flask.abort(403)
    upload_folder = insta485.app.config['UPLOAD_FOLDER']
    return flask.send_from_directory(upload_folder, filename)

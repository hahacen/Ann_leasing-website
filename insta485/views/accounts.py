"""
Insta485 accounts view.

URLs include:
/accounts/create/
/accounts/delete/
/accounts/edit/
/accounts/password/
/accounts/auth/
/accounts/?target=URL
"""

import pathlib
import uuid
import hashlib
import flask
import insta485
from insta485.api.service_api import requires_auth, raise_forbidden


@insta485.app.before_request
def require_login():
    """Give the guest user list they can visit."""
    # List of routes that don't require authentication
    whitelist = ['/accounts/login/', '/accounts/create/', '/accounts/auth/', '/']

    def is_exempted_route(path):
        """Check if the path is among the exempted routes."""
        exempted_starts = ["/uploads/", "/api/v1/", "/insta485/static/"]
        return any(
            path.startswith(route_start) for route_start in exempted_starts
            )

    # If the current route is not in the whitelist and user is not logged in
    if (not is_exempted_route(flask.request.path)
            and flask.request.method == 'GET'
            and flask.request.path not in whitelist
            and 'username' not in flask.session):
        # Redirect the user to the login page
        return flask.redirect(flask.url_for('accounts_login'))
    return None


@insta485.app.route('/accounts/login/')
def accounts_login():
    """Display /accounts/login/ route."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("login.html",)


@insta485.app.route('/accounts/logout/')
def accounts_logout():
    """Accept POST request to /accounts/logout/."""
    flask.session.clear()
    return flask.redirect(flask.url_for('accounts_login'))


@insta485.app.route('/accounts/create/')
def accounts_create():
    """Display /accounts/create/ route."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('accounts_edit'))

    return flask.render_template("create.html",)


@insta485.app.route('/accounts/delete/')
def accounts_delete():
    """Display /accounts/delete/ route."""
#    if 'username' not in flask.session:
#        return flask.redirect(flask.url_for('accounts_login'))

    username = flask.session['username']

    context = {'username': username}

    return flask.render_template("delete.html", **context)


@insta485.app.route('/accounts/edit/')
def accounts_edit():
    """Display /accounts/edit/ route."""
#    if 'username' not in flask.session:
#        return flask.redirect(flask.url_for('accounts_login'))

    username = flask.session['username']

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT fullname, filename, email FROM users WHERE username = ?",
        (username, )
    )
    user = cur.fetchone()
    context = {'username': username,
               'user': user}

    return flask.render_template("edit.html", **context)


@insta485.app.route('/accounts/password/')
def accounts_password():
    """Display /accounts/password/ route."""
#    if 'username' not in flask.session:
#        return flask.redirect(flask.url_for('accounts_login'))

    username = flask.session['username']
    context = {'username': username}

    return flask.render_template("password.html", **context)


@insta485.app.route('/accounts/auth/', methods=['GET'])
def accounts_auth():
    """GET /accounts/auth/ route."""
    logname = requires_auth()
    if not logname:
        raise_forbidden()
    return '', 200


@insta485.app.route('/accounts/', methods=['POST'])
def accounts():
    """Handle POST action to /accounts/."""
    operation = flask.request.form.get('operation')
    target = flask.request.args.get('target', '/')
    connection = insta485.model.get_db()

    if operation == "login":
        handle_login(connection=connection)

    if operation == "create":
        handle_create(connection=connection)

    if operation == "delete":
        handle_delete(connection=connection)

    if operation == "edit_account":
        handle_edit_account(connection=connection)

    if operation == "update_password":
        handle_update_password(connection=connection)

    return flask.redirect(target)


def handle_login(connection):
    """Handle login operation."""
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    if not username or not password:
        flask.abort(400)

    cur = connection.execute(
        "SELECT username, password "
        "FROM users "
        "WHERE username = ?",
        (username, )
    )
    user = cur.fetchone()
    if not user:
        flask.abort(403)

    password_info = user['password'].split("$")
    algorithm = password_info[0]
    salt = password_info[1]
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    if password_hash != password_info[2]:
        flask.abort(403)

    flask.session['username'] = user['username']


def handle_create(connection):
    """Handle create operation."""
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    fullname = flask.request.form.get('fullname')
    email = flask.request.form.get('email')
    fileobj = flask.request.files["file"]
    if not (username and password and fullname and email and fileobj):
        flask.abort(400)

    cur = connection.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    if cur.fetchone():
        flask.abort(409)

    filename = fileobj.filename
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)

    password_db_string = hash_password(password)

    cur.execute(
        "INSERT INTO users "
        "(username, password, fullname, email, filename) "
        "VALUES (?, ?, ?, ?, ?)",
        (username, password_db_string, fullname, email, uuid_basename,)
    )

    flask.session['username'] = username


def hash_password(password):
    """Hash the given password."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    return "$".join([algorithm, salt, password_hash])


def handle_delete(connection):
    """Handle delete operation."""
    if 'username' not in flask.session:
        flask.abort(403)

    username = flask.session['username']

    cur = connection.execute(
        "SELECT filename FROM users WHERE username = ? ",
        (username,)
    )
    filename = cur.fetchone()['filename']
    # delete user image from file system
    path = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"]/filename)
    path.unlink()

    cur = connection.execute(
        "SELECT filename FROM posts WHERE owner = ? ",
        (username,)
    )
    filename = cur.fetchall()
    for file in filename:
        file = file['filename']
        # delete user post image from file system
        path = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"]/file)
        path.unlink()

    connection.execute(
        "DELETE FROM users WHERE username = ?",
        (username,)
    )
    flask.session.clear()


def handle_edit_account(connection):
    """Handle edit account operation."""
    if 'username' not in flask.session:
        flask.abort(403)

    username = flask.session['username']
    fullname = flask.request.form.get('fullname')
    email = flask.request.form.get('email')
    fileobj = flask.request.files["file"]
    if not (fullname and email):
        flask.abort(400)

    if fileobj:
        cur = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (username,)
        )
        user = cur.fetchone()
        path = pathlib.Path(
            insta485.app.config["UPLOAD_FOLDER"]/user['filename'])
        path.unlink()

        filename = fileobj.filename
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        connection.execute(
            "UPDATE users SET fullname=?, email=?, filename=? "
            "WHERE username = ? ",
            (fullname, email, uuid_basename, username,)
        )
    else:
        connection.execute(
            "UPDATE users SET fullname=?, email=? "
            "WHERE username = ? ",
            (fullname, email, username,)
        )


def handle_update_password(connection):
    """Handle update password operation."""
    if 'username' not in flask.session:
        flask.abort(403)
    username = flask.session['username']
    password = flask.request.form.get('password')
    new_password1 = flask.request.form.get('new_password1')
    new_password2 = flask.request.form.get('new_password2')

    if not password or not new_password1 or not new_password2:
        flask.abort(400)

    cur = connection.execute(
        "SELECT username, password "
        "FROM users "
        "WHERE username = ?",
        (username, )
    )
    user = cur.fetchone()

    password_info = user['password'].split("$")
    algorithm = password_info[0]
    salt = password_info[1]
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    if password_hash != password_info[2]:
        flask.abort(403)

    if new_password1 != new_password2:
        flask.abort(401)

    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + new_password1
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    connection.execute(
        "UPDATE users "
        "SET password = ? "
        "WHERE username = ? ",
        (password_db_string, username, )
    )

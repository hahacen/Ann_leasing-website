"""REST API for v1 page and http command line auth."""
import hashlib
import flask
import leaseAnn


def check_auth(username, password):
    """Check if a username / password combination is valid."""
    connection = leaseAnn.model.get_db()
    cur = connection.execute(
        'SELECT password FROM users WHERE username=?', (username,)
    )
    result = cur.fetchone()
    if not result:
        return False
    stored_password = result['password']
    salt = stored_password.split("$")[1]
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    if result['password'] == password_db_string:
        return True
    return False


def raise_forbidden():
    """Send a 403 response that enables basic auth."""
    message = {"message": "Forbidden", "status_code": 403}
    resp = flask.jsonify(message)
    resp.status_code = 403
    return resp

# def requires_auth(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth = flask.request.authorization
#         if not auth or not check_auth(auth.username, auth.password):
#             return authenticate()
#         return f(*args, **kwargs)
#     return decorated


def requires_auth():
    """Check either cookie or http auth."""
    # Check cookie first
    logname = ''
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        # Check http auth
        auth = flask.request.authorization
        if auth and check_auth(auth.username, auth.password):
            logname = auth.username
    return logname


@leaseAnn.app.route('/api/v1/')
def get_service_list():
    """Return a list of services available."""
    # no login check
    service_list = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(service_list), 200


def get_authenticated_db_connection():
    """Authenticate database connection."""
    logname = requires_auth()
    if not logname:
        return None, raise_forbidden()
    connection = leaseAnn.model.get_db()
    return logname, connection

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
# TODO: submit post button

@insta485.app.route('/post_lease/')
def post_lease():

    return flask.render_template("post_lease.html")
@insta485.app.route('/post1/')
def show_post1():
    return flask.render_template("post1.html")

@insta485.app.route('/rent/')
def rent_page():
    return flask.render_template("rent.html")
@insta485.app.route('/starred_posts/')
def show_star():
    return flask.render_template("starred_posts.html")

@insta485.app.route('/my_posts/')
def show_my_post():
    return flask.render_template("my_posts.html")

@insta485.app.route('/submit_post/')
def submit_post():
    # Assuming the user is logged in and their username is stored in session
    logname = flask.session['username']

    # Connect to the database
    connection = insta485.model.get_db()

    # Get form data
    apartment = flask.request.form['apartment']
    price_range = flask.request.form['priceRange']
    name_in_post = flask.request.form['namePost']
    date = flask.request.form['date']
    descriptions = flask.request.form['descriptions']
    contact = flask.request.form['contact']

    # Handle file upload
    pictures = flask.request.files.getlist('pictures')
    picture_filenames = []
    for picture in pictures:
        # Ensure the file has a filename
        if picture.filename != '':
            # Save each picture
            filename = secure_filename(picture.filename)
            picture.save(os.path.join(insta485.app.config['UPLOAD_FOLDER'], filename))
            picture_filenames.append(filename)

    # Insert post into the database
    query = '''
    INSERT INTO posts (owner, apartment, price, date, descriptions, contact, filename)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    for filename in picture_filenames:
        connection.execute(query, (logname, apartment, price_range, date, descriptions, contact, filename))

    # Commit the changes
    connection.commit()

    # Redirect to the target URL or the user's page if no target URL is provided
    target_url = flask.request.args.get('target', f"/users/{logname}/")
    return flask.redirect(target_url)


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
        (postid_url_slug,)
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


# TODO: post new lease here
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
        path = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"] / filename)
        path.unlink()

        cur = connection.execute(
            'DELETE FROM posts '
            'WHERE owner = ? '
            'AND postid = ?',
            (logname, postid,)
        )
    return flask.redirect(target_url)

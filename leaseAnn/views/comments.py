"""
Insta485 comments' route.

URLs include:
/comments/
"""
import flask
import insta485


@insta485.app.route('/comments/', methods=['POST'])
def comments_button():
    """Operate various actions for comments."""
    logname = flask.session['username']
    connection = insta485.model.get_db()
    target_url = flask.request.args.get('target')
    operation = flask.request.form.get('operation')
    post_id = flask.request.form.get('postid')
    comment_id = flask.request.form.get('commentid')
    text = flask.request.form.get('text')
    # If the value of ?target is not set, redirect to /
    if not target_url:
        target_url = '/'
    # create operation
    if operation == "create":
        if not text:
            # Check for empty comment
            flask.abort(400, "Comment content cannot be empty")
        cur = connection.execute(
            'INSERT INTO comments '
            '(owner, postid, text) VALUES (?, ?, ?)',
            (logname, post_id, text,)
        )
    # delete operation
    elif operation == "delete":
        # Check if the user is the owner of the comment
        cur = connection.execute(
            'SELECT owner FROM comments WHERE commentid = ?', (comment_id,)
        )
        owner = cur.fetchone()
        if owner['owner'] != logname:
            flask.abort(403, "Unauthorized to delete this comment")
        # Delete the comment
        connection.execute(
            'DELETE FROM comments WHERE commentid = ?', (comment_id,)
        )
    return flask.redirect(target_url)

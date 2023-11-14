"""
Insta485 likes route.

URLs include:
/likes/
"""
import flask
import insta485


@insta485.app.route('/likes/', methods=['POST'])
def like_button():
    """Operate like or unlike a post."""
    # need Query database
    logname = flask.session['username']
    connection = insta485.model.get_db()
    target_url = flask.request.args.get('target')
    operation = flask.request.form.get('operation')
    post_id = flask.request.form['postid']
    if operation == "like":
        cur = connection.execute(
            'SELECT * FROM likes '
            'WHERE owner = ? '
            'AND postid = ? ', (logname, post_id,)
        )
        if cur.fetchone():
            flask.abort(409)

        cur = connection.execute(
            'INSERT INTO likes '
            '(owner, postid) '
            'VALUES (?, ?)',
            (logname, post_id,)
        )
    elif operation == "unlike":
        cur = connection.execute(
            'SELECT * FROM likes '
            'WHERE owner = ? '
            'AND postid = ? ', (logname, post_id,)
        )
        if not cur.fetchone():
            flask.abort(409)

        cur = connection.execute(
            'DELETE FROM likes '
            'WHERE owner = ? '
            'AND postid = ?',
            (logname, post_id,)
        )

    return flask.redirect(target_url)

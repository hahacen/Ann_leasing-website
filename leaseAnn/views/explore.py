"""
Insta485 explore view.

URLs include:
/explore/
"""
import flask
import insta485


@insta485.app.route('/explore/')
def show_explore():
    """Display /explore/."""
    connection = insta485.model.get_db()
    logname = flask.session['username']
    cur = connection.execute(
        "SELECT username, filename "
        "FROM users "
        "WHERE username != ? "
        "AND username NOT IN ( "
        "SELECT username2 FROM following WHERE username1 = ?) ",
        (logname, logname)
    )
    not_following = cur.fetchall()
    context = {"not_following": not_following,
               "logname": logname}
    return flask.render_template("explore.html", **context)

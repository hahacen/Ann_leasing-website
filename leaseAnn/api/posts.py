"""REST API for posts."""
import flask
import leaseAnn
from .service_api import (requires_auth,
                          raise_forbidden, get_authenticated_db_connection)


@leaseAnn.app.route('/api/v1/posts/')
def get_posts():
    """Get posts api."""
    logname = requires_auth()
    if not logname:
        return raise_forbidden()

    postid_lte, size, page = get_query_parameters()
    if size < 0 or page < 0:
        return bad_request_response()

    posts_info = fetch_posts(logname, postid_lte, size, page)

    response = construct_response(posts_info, size, page, postid_lte)
    return flask.jsonify(response), 200


def get_query_parameters():
    """Help get post api parameter."""
    postid_lte = flask.request.args.get("postid_lte", default=None, type=int)
    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)
    return postid_lte, size, page


def bad_request_response():
    """Help get post return bad request."""
    return flask.jsonify({
        "message": "Bad Request", "status_code": 400
    }), 400


def fetch_posts(logname, postid_lte, size, page):
    """Help get post fetch post."""
    connection = leaseAnn.model.get_db()
    query, params = construct_query(logname, postid_lte, size, page)
    cur = connection.execute(query, params)
    posts = cur.fetchall()
    return [{
        "postid": post["postid"],
        "url": f"/api/v1/posts/{post['postid']}/"
    } for post in posts]


def construct_query(logname, postid_lte, size, page):
    """Help get post construct query."""
    non_spe = (
        "SELECT posts.* "
        "FROM posts "
        "WHERE owner IN ( "
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ? )"
        "OR owner = ? "
    )
    postid_q = "AND postid <= ? " if postid_lte else ""
    page_size_q = "ORDER BY postid DESC LIMIT ? OFFSET ? "
    query = f"{non_spe} {postid_q} {page_size_q}"
    params = [logname, logname]
    if postid_lte:
        params.append(postid_lte)
    params.extend([size, size * page])
    return query, params


def construct_response(posts_info, size, page, postid_lte):
    """Help get post append response."""
    next_url = construct_next_url(posts_info, size, page, postid_lte)
    constructed_url = construct_current_url(size, page, postid_lte)

    return {
        "next": next_url,
        "results": posts_info,
        "url": constructed_url
    }


def construct_next_url(posts_info, size, page, postid_lte):
    """Help get post construct next url."""
    if len(posts_info) < size:
        return ""

    next_params = f"size={size}&page={page + 1}"
    largest_postid = postid_lte if postid_lte else posts_info[0]['postid']
    next_params += f"&postid_lte={largest_postid}"
    return f"/api/v1/posts/?{next_params}"


def construct_current_url(size, page, postid_lte):
    """Help get post construct current url."""
    base_url = "/api/v1/posts/"
    params_list = []
    if size:
        params_list.append(f"size={size}")
    if page:
        params_list.append(f"page={page}")
    if postid_lte:
        params_list.append(f"postid_lte={postid_lte}")
    return (
        base_url + "?" + "&".join(params_list)
        if flask.request.args else base_url
           )


@leaseAnn.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post on postid.

    Example:
    {
      "created": "2017-09-28 04:33:28",
      "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
      "owner": "awdeorio",
      "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
      "ownerShowUrl": "/users/awdeorio/",
      "postShowUrl": "/posts/1/",
      "url": "/api/v1/posts/1/"
    }
    """
    # Login check
    logname, connection = get_authenticated_db_connection()

    # Post information
    cur = connection.execute(
            "SELECT owner, filename, created "
            "FROM posts WHERE postid = ? ",
            (postid_url_slug,)
    )
    post = cur.fetchone()
    if not post:
        return '', 404
    post["imgUrl"] = f"/uploads/{post['filename']}"
    post.pop("filename")
    post["postShowUrl"] = f"/posts/{postid_url_slug}/"
    post["postid"] = postid_url_slug
    post["url"] = flask.request.path

    # Owner information
    cur = connection.execute(
            "SELECT filename FROM users WHERE username = ? ",
            (post["owner"],)
    )
    owner = cur.fetchone()
    post["ownerImgUrl"] = f"/uploads/{owner['filename']}"
    post["ownerShowUrl"] = f"/users/{post['owner']}/"

    # Comments
    cur = connection.execute(
            "SELECT commentid, owner, text "
            "FROM comments WHERE postid = ? ",
            (postid_url_slug,)
    )
    comments = cur.fetchall()
    post["comments"] = []
    for comment in comments:
        comment["lognameOwnsThis"] = \
                logname == comment["owner"]
        comment["ownerShowUrl"] = f"/users/{comment['owner']}/"
        comment["url"] = f"/api/v1/comments/{comment['commentid']}/"
        post["comments"].append(comment)
    post["comments_url"] = \
        f"/api/v1/comments/?postid={postid_url_slug}"

    # Likes
    cur = connection.execute(
            "SELECT COUNT(*) as numLikes FROM likes WHERE postid = ?",
            (postid_url_slug,)
    )
    like = cur.fetchone()
    cur = connection.execute(
            "SELECT likeid FROM likes WHERE postid = ? and owner = ?",
            (postid_url_slug, logname,)
    )
    logname_like = cur.fetchone()
    post["likes"] = {
            "lognameLikesThis": bool(logname_like),
            "numLikes": like["numLikes"],
            "url": f"/api/v1/likes/{logname_like['likeid']}/"
            if logname_like else None
    }

    context = post
    return flask.jsonify(**context), 200

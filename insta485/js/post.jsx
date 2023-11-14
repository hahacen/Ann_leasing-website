import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";

dayjs.extend(relativeTime);
dayjs.extend(utc);

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [imgUrl, setImgUrl] = useState("");
  const [created, setCreated] = useState("");
  const [showUrl, setShowUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [postid, setPostid] = useState("");
  const [ownerImgUrl, setownerImgUrl] = useState("");
  const [numLikes, setNumLikes] = useState("");
  // this is for like/unlike switch
  const [isLiked, setIsLiked] = useState(false);
  const [likeText, setLikeText] = useState("");
  // this is for likes url
  const [likesUrl, setLikesUrl] = useState({});
  const [rendered, setRendered] = useState(false);

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          const numLikesValue = data.likes.numLikes;
          const likeTextValue = numLikesValue === 1 ? "like" : "likes";
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setPostid(data.postid);
          setCreated(data.created);
          setShowUrl(data.postShowUrl);
          setownerImgUrl(data.ownerImgUrl);
          setNumLikes(numLikesValue);
          setLikeText(likeTextValue);
          setIsLiked(data.likes.lognameLikesThis);
          setLikesUrl(data.likes.url);
          setRendered(true);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  // handle like and unlike button
  const handleToggleLike = () => {
    if (isLiked) {
      setIsLiked(false);
      const likeTextVal = numLikes - 1 === 1 ? "like" : "likes";
      setNumLikes((prevLikes) => prevLikes - 1);
      setLikeText(likeTextVal);
      setLikesUrl(null);
      console.log("function triggered");
      // User currently likes the post and wants to unlike it.
      // Make an API call to DELETE the like on the server.
      fetch(likesUrl, {
        method: "DELETE",
        credentials: "same-origin",
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          console.log("delete triggered");
        })
        .catch((error) =>
          console.error(
            "There was a problem with the fetch operation:",
            error.message,
          ),
        );
    } else {
      // User currently does not like the post and wants to like it.
      // Make an API call to POST the like on the server.
      setIsLiked(true);
      const likeTextVal = numLikes + 1 === 1 ? "like" : "likes";
      setNumLikes((prevLikes) => prevLikes + 1);
      setLikeText(likeTextVal);
      fetch(`/api/v1/likes/?postid=${postid}`, {
        method: "POST",
        credentials: "same-origin",
      })
        .then((response) => {
          if (response.ok) {
            return response.json();
          }
          throw new Error();
        })
        .then((data) => {
          setLikesUrl(data.url);
          console.log("insert like triggered");
        })
        .catch((error) =>
          console.error(
            "There was a problem with the fetch operation:",
            error.message,
          ),
        );
    }
  };
  const createdHr = dayjs(created).utc().fromNow();

  // Render post image and post owner
  if (!rendered) {
    return <div>Loading...</div>;
  }
  return (
    <div className="post">
      <p>{owner}</p>
      <a href={`/users/${owner}/`}>
        <img
          src={ownerImgUrl}
          alt="owner_image"
          style={{ width: "50px", height: "50px" }}
        />
      </a>
      {/* here is the implementation of the double click and showing the image */}
      <img
        src={imgUrl}
        alt="post_image"
        onDoubleClick={() => {
          if (!isLiked) {
            handleToggleLike();
          }
        }}
      />

      <a href={showUrl}>
        <p>{createdHr}</p>
      </a>
      <p>
        {numLikes} {likeText}
      </p>
      {/* here is the implementation of the double click */}

      <button
        type="button"
        data-testid="like-unlike-button"
        onClick={handleToggleLike}
      >
        {isLiked ? "Unlike" : "Like"}
      </button>
      <Comments postUrl={url} />
    </div>
  );
}

function Comments({ postUrl }) {
  const [commentText, setCommentText] = useState("");
  const [comments, setComments] = useState([]);
  const [commentsUrl, setCommentsUrl] = useState({});
  const [submit, setSubmit] = useState(0);
  const [rendered, setRendered] = useState(false);

  // const [error, setError] = useState(null);
  // const [status, setStatus] = useState("typing");

  useEffect(() => {
    fetch(
      postUrl,
      {
        credentials: "same-origin",
      },
      setSubmit(0),
    )
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        throw Error(response.status);
      })
      .then((data) => {
        setRendered(true);
        setComments(data.comments);
        setCommentsUrl(data.comments_url);
      });
  }, [submit, postUrl]);

  function handleSubmit(e) {
    e.preventDefault();
    setSubmit(1);
    fetch(commentsUrl, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: commentText }),
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        throw Error(response.status);
      })
      .then(() => {
        setCommentText("");
      });
  }

  function handleTextChange(e) {
    e.preventDefault();
    setCommentText(e.target.value);
  }

  function handleDelete(commentId) {
    fetch(`/api/v1/comments/${commentId}/`, {
      method: "DELETE",
      credentials: "same-origin",
    })
      .then((response) => {
        if (response.ok) {
          // Remove the deleted comment from the local state
          const updatedComments = comments.filter(
            (comment) => comment.commentid !== commentId,
          );
          setComments(updatedComments);
        } else {
          // Handle the error. You can throw it or handle it differently based on your requirements.
          throw new Error("Error deleting the comment");
        }
      })
      .catch((error) => {
        // Log the error or show an error message to the user.
        console.error("Error:", error);
      });
  }
  if (!rendered) {
    return <div>Loading...</div>;
  }
  return (
    <div className="comments">
      {comments.map((comment) => (
        <div
          key={comment.commentid}
          className="comment"
          data-testid="comment-text"
        >
          <p>
            <strong>
              <a href={`/users/${comment.owner}/`}>{comment.owner}</a>:
            </strong>
            {comment.text}
          </p>
          {comment.lognameOwnsThis && (
            <button
              type="button"
              onClick={() => handleDelete(comment.commentid)}
              data-testid="delete-comment-button"
            >
              Delete
            </button>
          )}
        </div>
      ))}
      <form data-testid="comment-form" onSubmit={handleSubmit}>
        <input type="text" value={commentText} onChange={handleTextChange} />
      </form>
    </div>
  );
}

Comments.propTypes = {
  postUrl: PropTypes.string.isRequired,
};

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post";

const root = createRoot(document.getElementById("reactEntry"));

export default function Main() {
  // next_post is url, while post is the result contents
  const [posts, setPosts] = useState([]);
  // temporarily hard code
  // const [post_lte, setlte] = useState([104])
  const [nextPosts, setNextPosts] = useState("/api/v1/posts/");
  const [hasNext, setHasNext] = useState(true);
  const [rendered, setRendered] = useState(false);

  //   function extractPostIdLteFromUrl(post_url) {
  //   const parsedUrl = new URL(post_url, window.location.origin); // Assuming the URL might be a relative path
  //   const postidLte = parsedUrl.searchParams.get("postid_lte");
  //   return postidLte ? parseInt(postidLte) : null;
  // }

  const fetchPost = () => {
    fetch(nextPosts, { credentials: "same-origin" })
      .then(
        (response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        },
        console.log("fetching", nextPosts),
      )
      .then((data) => {
        setPosts([...posts, ...data.results]);
        setNextPosts(data.next);
        setHasNext(data.next !== "");
        setRendered(true);
      });
  };
  //   const fecthPost = (post_url)=>{
  //       fetch(post_url, { credentials: "same-origin" })
  //           .then(response => {
  //               if (!response.ok) throw Error(response.statusText);
  //               return response.json();
  //           })
  //           .then(data => {
  //             console.log("API Response:", data);
  //             setPosts(prevPosts => [...prevPosts, ...data.results]);
  //             set_next(data.next)
  //               // // console.log(data.next)
  //               // console.log("post_url",data.next);
  //               // console.log("API Response:", data);
  //           })
  //           .catch(error => console.log(error))
  //   }

  useEffect(() => {
    fetchPost();
    console.log("useeffect fetch");
  }, []);

  if (!rendered) {
    return <div>Loading...</div>;
  }
  return (
    <InfiniteScroll
      next={fetchPost}
      hasMore={hasNext}
      loader={<h4>Loading...</h4>}
      dataLength={posts.length}
      initialLoad={false} // avoid the initial loading trigger
    >
      {posts.map((post) => (
        <Post key={post.postid} url={post.url} />
      ))}
    </InfiniteScroll>
  );
}

root.render(
  // <StrictMode>
  <Main />,
  /* </StrictMode>, */
);

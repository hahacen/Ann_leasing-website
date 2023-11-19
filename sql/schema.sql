PRAGMA foreign_keys = ON;

CREATE TABLE users(
  username VARCHAR(20) NOT NULL,  
  fullname VARCHAR(40) NOT NULL,
  email VARCHAR(40) NOT NULL,
  filename VARCHAR(64) NOT NULL,
  password VARCHAR(256) NOT NULL,
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(username) /* Declare the index */
);

CREATE TABLE posts(
  postid INTEGER PRIMARY KEY AUTOINCREMENT,
  filename VARCHAR(64) NOT NULL,
  owner VARCHAR(20) NOT NULL,
  apartment VARCHAR(20) NOT NULL,
  price VARCHAR(40) NOT NULL,
  address VARCHAR(40) NOT NULL,
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(owner) REFERENCES users(username) ON DELETE CASCADE /* borrow the index from user (not really for indexing), do not have to clarify the reference if the index name is the same */
);

CREATE TABLE starred_posts(
  starid INTEGER PRIMARY KEY AUTOINCREMENT,
  username VARCHAR(20) NOT NULL,
  postid INTEGER NOT NULL,
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE,
  FOREIGN KEY(postid) REFERENCES posts(postid) ON DELETE CASCADE
);

CREATE TABLE apartment(
    apartmentid INTEGER PRIMARY KEY AUTOINCREMENT,
    apartment VARCHAR(40) NOT NULL,
    description  VARCHAR(40) NOT NULL,
    filename ARCHAR(64) NOT NULL,
    link VARCHAR(40) NOT NULL
);
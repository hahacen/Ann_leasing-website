PRAGMA foreign_keys = ON;

INSERT INTO users(username, fullname, email, filename, password)
VALUES ('awdeorio', 'Andrew DeOrio', 'awdeorio@umich.edu', 
    'e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');

INSERT INTO users(username, fullname, email, filename, password)
VALUES ('jflinn', 'Jason Flinn', 'jflinn@umich.edu', 
'505083b8b56c97429a728b68f31b0b2a089e5113.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');


INSERT INTO users(username, fullname, email, filename, password)
VALUES ('michjc', 'Michael Cafarella', 'michjc@umich.edu', 
'5ecde7677b83304132cb2871516ea50032ff7a4f.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');

INSERT INTO users(username, fullname, email, filename, password)
VALUES ('jag', 'H.V. Jagadish', 'jag@umich.edu', 
    '73ab33bd357c3fd42292487b825880958c595655.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');

INSERT INTO posts(filename, owner, apartment, price, address)
VALUES ('122a7d27ca1d7420a1072f695d9290fad4501a41.jpg', 'awdeorio', 'The One', '1000', '2316 Erie Dr');

INSERT INTO posts(filename, owner, apartment, price, address)
VALUES ('ad7790405c539894d25ab8dcf0b79eed3341e109.jpg', 'jflinn', 'Willowtree', '800', '1853 Lake Lila ln');

INSERT INTO posts(filename, owner, apartment, price, address)
VALUES ('9887e06812ef434d291e4936417d125cd594b38a.jpg', 'awdeorio', 'Courtyard', '1100', '287 Courtyard Dr');

INSERT INTO posts(filename, owner, apartment, price, address)
VALUES ('2ec7cf8ae158b3b1f40065abfb33e81143707842.jpg', 'jag', 'Willowtree', '900', '1822 Happy Ln');

INSERT INTO starred_posts(username, postid)
VALUES ('awdeorio', 1);

INSERT INTO starred_posts(username, postid)
VALUES ('michjc', 1);

INSERT INTO starred_posts(username, postid)
VALUES ('jflinn', 1);

INSERT INTO starred_posts(username, postid)
VALUES ('awdeorio', 2);

INSERT INTO starred_posts(username, postid)
VALUES ('michjc', 2);

INSERT INTO starred_posts(username, postid)
VALUES ('awdeorio', 3);

INSERT INTO apartment(apartment, description, link, filename)
VALUES ('The One', 'The One is Ann Arbor''s only off-campus student living that offers houses and townhomes with porches, well-manicured yards and resident + guest parking in front of your residence',
        'https://www.theoneannarbor.com/',
        'something');

INSERT INTO apartment(apartment, description, link, filename)
VALUES ('Willowtree', 'Right next to The University of Michigan and right in your budget! Willowtree Apartments & Tower gives you the student lifestyle you want at a price you can afford in Ann Arbor! ',
        'https://www.americancampus.com/student-apartments/mi/ann-arbor/willowtree-apartments-tower',
        'something');

INSERT INTO apartment(apartment, description, link, filename)
VALUES ('Courtyard', 'Off-Campus Student Housing near University of Michigan North Campus',
        'https://www.sterlinghousing.com/ann-arbor-mi/the-courtyards',
        'something');

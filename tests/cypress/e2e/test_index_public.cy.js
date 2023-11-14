// This is a Cypress spec. Each describe() block is a group of tests.
// Each it() block is a single test.

// This is a helper function for loading the feed. We call inside tests when we need to make sure
// that the page has fully loaded.
function loadFeed() {
  // Intercept calls to the /api/v1/posts/ route and store a Route Alias
  // called getPosts. Later, we can refer to requests to this route using getPosts.
  cy.intercept("GET", "/api/v1/posts/").as("getPosts");

  // Go to the home page.
  cy.visit("/");

  // Verify that a request was made to /api/v1/posts/.
  cy.wait("@getPosts");

  // Verify links. Each call to cy.get() is an implicit assertion that an element matching
  // the selector exists.
  cy.get("a[href='/posts/1/']");
  cy.get("a[href='/posts/2/']");
  cy.get("a[href='/posts/3/']");
  cy.get("a[href='/users/awdeorio/']");
  cy.get("a[href='/users/jflinn/']");
  cy.get("a[href='/users/michjc/']");

  // Verify images.
  cy.get("img[src='/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg']");
  cy.get("img[src='/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg']");
  cy.get("img[src='/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg']");
  cy.get("img[src='/uploads/ad7790405c539894d25ab8dcf0b79eed3341e109.jpg']");
  cy.get("img[src='/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg']");

  // Verify text. Each call to cy.contains() is an implicit assertion that the text appears
  // somewhere on the page.
  cy.contains("#chickensofinstagram");
  cy.contains("I <3 chickens");
  cy.contains("Cute overload");
  cy.contains("Sick #crossword");
  cy.contains("Walking the plank #chickensofinstagram");
  cy.contains("This was after trying to teach them to do a #crossword");
}

describe("Index page when awdeorio is logged in with real database", () => {
  // The beforeEach() hook automatically runs before each it() block.
  beforeEach(() => {
    // Reset the database. This command is equivalent to running ./insta485db reset.
    cy.task("seedDb");

    // Log in at the beginning of every test.
    cy.login("awdeorio", "password");
  });

  it("Loads the index page feed including links, images, and comment text on normal server", () => {
    loadFeed();
  });

  it("Shows a new comment without a page refresh on normal server", () => {
    // Intercept calls to the /api/v1/comments/?postid=3 route and store a Route Alias
    // called newComment. Later, we can refer to requests to this route using newComment.
    cy.intercept("POST", "/api/v1/comments/?postid=3").as("newComment");

    // Go to the home page.
    cy.visit("/");

    // Find comment input field for postid 3. It should be the first one on the page,
    // so it should have index 0. Then type a comment into the input and press enter.
    cy.get("form[data-testid='comment-form'] input[type='text']")
      .should("have.length", 3)
      .eq(0)
      .type("test comment{enter}");

    // Verify that a request was made for creating the new comment.
    cy.wait("@newComment");

    // Verify that the new comment appears on the page.
    cy.contains("test comment");
  });

  it("Removes a comment from the UI after pressing the delete comment button on normal server", () => {
    // Intercept calls to the /api/v1/comments/1/ route and store a Route Alias
    // called deleteComment. Later, we can refer to requests to this route using deleteComment.
    cy.intercept("DELETE", "/api/v1/comments/1/").as("deleteComment");

    // Go to the home page.
    cy.visit("/");

    // Verify that there are 2 comments which say "#chickensofinstagram"
    cy.get(
      "[data-testid='comment-text']:contains(#chickensofinstagram)"
    ).should("have.length", 2);

    // Verify that there are 3 delete buttons and click the first one.
    // It should be for a comment that says "#chickensofinstagram".
    cy.get("button[data-testid='delete-comment-button']")
      .should("have.length", 3)
      .eq(0)
      .click();

    // Verify that a request was made for deleting the comment.
    cy.wait("@deleteComment");

    // Verify that there is one fewer comment with the text "#chickensofinstagram" than before.
    cy.get(
      "[data-testid='comment-text']:contains(#chickensofinstagram)"
    ).should("have.length", 1);

    // Verify that there is one fewer delete comment button than before.
    cy.get("button[data-testid='delete-comment-button']").should(
      "have.length",
      2
    );
  });

  it("Updates the UI when liking or unliking a post on normal server", () => {
    // Intercept calls to these routes and store aliases unlike and
    // newLike so that we can reference the requests later.
    cy.intercept("DELETE", "/api/v1/likes/6/").as("unlike");
    cy.intercept("POST", "/api/v1/likes/?postid=3").as("newLike");

    // Go to the home page.
    cy.visit("/");

    // Verify that the text "0 like" and "0 likes" don't appear on the page.
    // Every post should already have likes at this point.
    cy.contains("0 likes").should("not.exist");
    cy.contains("0 like").should("not.exist");

    // Verify that there are 3 like/unlike buttons and click the first one.
    cy.get("button[data-testid='like-unlike-button']")
      .should("have.length", 3)
      .eq(0)
      .click();

    // Verify that a request was made for unliking the post.
    cy.wait("@unlike");

    // Verify that a post now has 0 likes. Also verify that there are no
    // posts with 1 like anymore.
    cy.contains("0 likes");
    cy.contains("1 like").should("not.exist");

    // Click the first like button again.
    cy.get("button[data-testid='like-unlike-button']").eq(0).click();

    // Verify that a request was made for creating the new like.
    cy.wait("@newLike");

    // Verify that "1 like" appears on the page again, and check for a typo.
    cy.contains("1 like");
    cy.contains("1 likes").should("not.exist");
    cy.contains("0 likes").should("not.exist");
  });

  it("Renders to HTML5-compliant HTML code on normal server", () => {
    // Go to the index page and make sure the feed has loaded.
    loadFeed();

    // Run html5validator on the rendered page. First query for the top-level element,
    // <html>.
    cy.get("html")
      // This call retrieves the HTML code for the <html> element and all of its contents.
      .invoke("prop", "outerHTML")
      // This call gives us access to the HTML code in a callback function.
      .then((doc) => {
        // Add back <!DOCTYPE> because it's not contained inside the <html> element.
        let htmlCode = `<!DOCTYPE html>${doc}`;

        // Cypress adds a script inside the page. Strip it out so we don't include it
        // while running html5validator.
        htmlCode = htmlCode.replace(/<script.*<\/script>/, "");

        // Prettify the HTML code.
        cy.task("prettify", htmlCode).then((prettifiedHtmlCode) => {
          // Write the HTML code to a temporary file and run html5validator on it.
          cy.task("createTmpfile").then((tmpfile) => {
            cy.writeFile(tmpfile.name, prettifiedHtmlCode);
            cy.exec(
              `html5validator --ignore=JAVA_TOOL_OPTIONS ${tmpfile.name}`
            );
          });
        });
      });
  });
});

describe("Index page when awdeorio is logged in with mock database", () => {
  // The beforeEach() hook automatically runs before each it() block.
  beforeEach(() => {
    // Intercept calls to the /api/v1/posts/ route and store a Route Alias
    // called getPosts. Later, we can refer to requests to this route using getPosts.
    // We also *stub* these requests by stopping them from actually reaching our back-end
    // server. Instead, we load a hard-coded response from the file
    // cypress/fixtures/posts_page_0.json and send it back to the client.
    cy.intercept("GET", "/api/v1/posts/", { fixture: "posts_page_0.json" }).as(
      "getPosts"
    );

    // Intercept requests for 30 posts. These tests begin assuming that there are 30 tests
    // that already exist. Each request gets stubbed with a hard-coded response from
    // cypress/fixtures/post{i}.json where i is the postId.
    for (let i = 1; i < 31; i += 1) {
      cy.intercept("GET", `/api/v1/posts/${i}/`, {
        fixture: `posts/${i}.json`,
      });
    }

    // Stub requests for the upload images so that the UI looks more realistic.
    cy.intercept("GET", "/uploads/0d02a5a4bb6b460abf9160522ad9d324.png", {
      fixture: "uploads/0d02a5a4bb6b460abf9160522ad9d324.png",
    });
    cy.intercept("GET", "/uploads/4ef62485e76c4320af6085ac7822cc57.png", {
      fixture: "uploads/4ef62485e76c4320af6085ac7822cc57.png",
    });

    // Log in at the beginning of every test.
    cy.login("awdeorio", "password");
  });

  it("Updates the feed when refreshing after a new post is created on normal server", () => {
    // Go to the home page.
    cy.visit("/");

    // Wait until the client makes a request to /api/v1/posts/.
    cy.wait("@getPosts");

    // Verify that there are links on the page for posts with IDs between 21 and 30 inclusive.
    for (let i = 30; i >= 21; i -= 1) {
      cy.get(`a[href='/posts/${i}/']`);
    }

    // Verify that the very first post on the page is post 30.
    cy.get("a[href^='/posts/']")
      .eq(0)
      .should("have.attr", "href", "/posts/30/");

    // Make a new interception for /api/v1/posts/, now with two new posts. This overrides the
    // previous interception for this route.
    cy.intercept("GET", "/api/v1/posts/", {
      fixture: "posts_page_0_new_posts.json",
    }).as("getPosts");

    // Stub responses for the two new posts.
    cy.intercept("GET", "/api/v1/posts/31/", { fixture: "posts/31.json" });
    cy.intercept("GET", "/api/v1/posts/32/", { fixture: "posts/32.json" });

    // Refresh the page.
    cy.reload();

    // Wait until the client makes a request to /api/v1/posts/.
    cy.wait("@getPosts");

    // Verify that posts 23-32 inclusive now appear on the page.
    for (let i = 32; i >= 23; i -= 1) {
      cy.get(`a[href='/posts/${i}/']`);
    }

    // Verify that the very first post on the page is post 32.
    cy.get("a[href^='/posts/']")
      .eq(0)
      .should("have.attr", "href", "/posts/32/");

    // Verify that posts 21 and 22 no longer appear on the page after the refresh.
    cy.get("a[href='/posts/21/']").should("not.exist");
    cy.get("a[href='/posts/22/']").should("not.exist");
  });
});

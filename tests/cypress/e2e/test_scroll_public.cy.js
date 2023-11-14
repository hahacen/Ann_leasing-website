// This is a Cypress spec. Each describe() block is a group of tests.
// Each it() block is a single test.

describe("Infinite scroll", () => {
  // The beforeEach() hook automatically runs before each it() block.
  beforeEach(() => {
    // Intercept calls to the /api/v1/posts/ route for each page and store aliases.
    // Later, we can refer to requests to these using their aliases.
    // We also *stub* these requests by stopping them from actually reaching our back-end
    // server. Instead, we load a hard-coded response from a JSON file and send it back to the client.
    cy.intercept("GET", "/api/v1/posts/", { fixture: "posts_page_0.json" }).as(
      "getPostsPage0"
    );
    cy.intercept("GET", "/api/v1/posts/?size=10&page=1&postid_lte=30", {
      fixture: "posts_page_1.json",
    }).as("getPostsPage1");
    cy.intercept("GET", "/api/v1/posts/?size=10&page=2&postid_lte=30", {
      fixture: "posts_page_2.json",
    }).as("getPostsPage2");

    // Intercept requests for 30 posts. These tests begin assuming that there are 30 posts
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

  it("Loads a second page of posts after scrolling to the bottom of the screen on normal server", () => {
    // Go to the home page.
    cy.visit("/");

    // Wait until the client makes a request to /api/v1/posts/.
    cy.wait("@getPostsPage0");

    // Verify that there are links on the page for posts with IDs between 21 and 30 inclusive.
    for (let i = 30; i >= 21; i -= 1) {
      cy.get(`a[href='/posts/${i}/']`);
    }

    // Verify that only 10 posts appear on the page and the very first post is post 30.
    cy.get("a[href^='/posts/']")
      .should("have.length", 10)
      .eq(0)
      .should("have.attr", "href", "/posts/30/");

    // Scroll to the bottom of the page.
    cy.scrollTo("bottom");

    // Wait until the client makes a request for the posts on page 1.
    cy.wait("@getPostsPage1");

    // Verify that there are links on the page for the most recent 20 posts now.
    for (let i = 30; i >= 11; i -= 1) {
      cy.get(`a[href='/posts/${i}/']`);
    }

    // Verify that only 20 posts appear on the page and the very first post
    // is still post 30.
    cy.get("a[href^='/posts/']")
      .should("have.length", 20)
      .eq(0)
      .should("have.attr", "href", "/posts/30/");
  });
});

// ***********************************************
// This file is for creating custom commands and
// overwriting existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//

// Create a cy.login() command which takes two arguments, `username` and `password`.
Cypress.Commands.add("login", (username, password) => {
  // Create a session that uses the username and password as a cache ID. Cypress will restore this
  // session in later tests to avoid repeatedly logging in during each test.
  // See here for more info: https://docs.cypress.io/api/commands/session
  cy.session(
    [username, password],
    () => {
      cy.request({
        method: "POST",
        url: "/accounts/",
        form: true,
        body: {
          username,
          password,
          operation: "login",
        },
      })
        .its("status")
        .should("eq", 200);
    },
    {
      // Use this validate function when the session is restored to ensure that the test
      // is actually logged in.
      validate() {
        cy.request("/accounts/auth/").its("status").should("eq", 200);
      },
      // Cache this session even for tests in a different file.
      cacheAcrossSpecs: true,
    }
  );
});

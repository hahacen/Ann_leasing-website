// ***********************************************************
// This file is processed and loaded automatically before
// test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// Read more here:
// https://on.cypress.io/configuration
// ***********************************************************

/* eslint-disable import/no-extraneous-dependencies */

// Import any custom commands.
import "./commands";
import registerCypressGrep from "@cypress/grep/src/support";
import failOnConsoleError from "cypress-fail-on-console-error";

// Automatically fail any test if there are console errors.
failOnConsoleError();

// Load the cypress-grep feature so that we can use pattern-matching to determine
// which tests to run.
registerCypressGrep();

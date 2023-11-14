module.exports = {
  extends: ["airbnb", "plugin:cypress/recommended", "prettier"],
  plugins: ["react", "react-hooks", "jsx-a11y", "import"],
  env: {
    browser: true,
  },
  // Allow use of console.log()
  rules: {
    "no-console": 0,

    // Rules for React Hooks
    // https://reactjs.org/docs/hooks-rules.html#eslint-plugin
    "react-hooks/rules-of-hooks": "error", // Checks rules of Hooks
    "react-hooks/exhaustive-deps": "warn", // Checks effect dependencies

    // A specific rule for Cypress tests that disallows committing code with cy.pause()
    "cypress/no-pause": "error",
  },
  overrides: [
    {
      files: ["**/*.ts", "**/*.tsx"],
      parser: "@typescript-eslint/parser",
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
        ecmaVersion: "latest",
        sourceType: "module",
        project: "./tsconfig.json",
      },
      extends: ["airbnb", "airbnb-typescript", "prettier"],
      plugins: ["react", "react-hooks", "jsx-a11y", "import"],
      rules: {
        "no-console": 0,
        "react-hooks/rules-of-hooks": "error", // Checks rules of Hooks
        "react-hooks/exhaustive-deps": "warn", // Checks effect dependencies
      },
    },
  ],
};

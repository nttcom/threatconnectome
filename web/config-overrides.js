/* config-overrides.js */
/* eslint-disable react-hooks/rules-of-hooks */
const { useBabelRc, override } = require("customize-cra");

module.exports = {
  webpack: override(useBabelRc()),
  jest: (config) => {
    config.testEnvironment = "jest-environment-jsdom";
    config.setupFilesAfterEnv = ["<rootDir>/jest.setup.js"];
    config.moduleNameMapper = {
      "\\.css$": "<rootDir>/__mocks__/cssMock.js",
    };
    return config;
  },
};

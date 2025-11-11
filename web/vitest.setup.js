import "@testing-library/jest-dom/vitest";
import { setupServer } from "msw/node";
import { beforeAll, afterEach, afterAll } from "vitest";

// Set up the server. Handlers are added in individual tests.
export const server = setupServer();

// Start the server before all tests and throw an error for unhandled requests.
beforeAll(() => server.listen({ onUnhandledRequest: "warn" }));

// Reset any request handlers that we may add during the tests,
// so they don't affect other tests.
afterEach(() => server.resetHandlers());

// Clean up after the tests are finished.
afterAll(() => server.close());

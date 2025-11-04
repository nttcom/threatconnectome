import { createTheme, CssBaseline, ThemeProvider } from "@mui/material";
import { configureStore } from "@reduxjs/toolkit";
import { initialize, mswLoader } from "msw-storybook-addon";
import { SnackbarProvider } from "notistack";
import { Provider } from "react-redux";
import { MemoryRouter } from "react-router-dom";

import { AuthProvider } from "../src/providers/auth/AuthContext";
import { tcApi } from "../src/services/tcApi";
import { sliceReducers } from "../src/slices";

// Initialize MSW
initialize();

const mockAuthedState = {
  auth: {
    authUserIsReady: true,
  },
};

const rootReducer = {
  ...sliceReducers,
  [tcApi.reducerPath]: tcApi.reducer,
};

const theme = createTheme();

const decorators = [
  (Story, context) => {
    // Get the individual story's preloadedState
    const { preloadedState: storyPreloadedState } = context.parameters.redux || {};

    // Safely merge the default state (mockAuthedState) with the story-specific state (preloadedState)
    const preloadedState = {
      ...mockAuthedState, // 1. Apply default state for all slices
      ...storyPreloadedState, // 2. Override with story-specific slices (e.g., user: {})

      // 3. Deep-merge the 'auth' slice specifically
      // This ensures 'authUserIsReady: true' is the default,
      // but allows stories to override it (e.g., authUserIsReady: false for login screen)
      // or extend it (e.g., auth: { ... , role: 'admin' })
      auth: {
        ...mockAuthedState.auth,
        ...(storyPreloadedState?.auth || {}),
      },
    };

    const store = configureStore({
      reducer: rootReducer,
      preloadedState,
      middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(tcApi.middleware),
    });

    // --- IMPORTANT: Force remount on args change ---
    // RTK Query caches data. When args change in Controls, RTK Query hooks
    // might keep stale data or a 'loading' state, freezing the component.
    // Changing the 'key' forces React to remount the entire tree,
    // creating a new, fresh store and clearing all RTK Query cache.
    // This is the simplest way to ensure Controls work reliably with RTK Query.
    const key = JSON.stringify(context.args) + "-" + context.globals.viewport.value;

    return (
      <MemoryRouter>
        <AuthProvider>
          <Provider key={key} store={store}>
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <SnackbarProvider>
                <Story />
              </SnackbarProvider>
            </ThemeProvider>
          </Provider>
        </AuthProvider>
      </MemoryRouter>
    );
  },
];

/** @type { import('@storybook/react-vite').Preview } */
const preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },

    a11y: {
      // 'todo' - show a11y violations in the test UI only
      // 'error' - fail CI on a11y violations
      // 'off' - skip a11y checks entirely
      test: "todo",
    },
  },
  // Provide the MSW addon loader globally
  loaders: [mswLoader],
  decorators,
};

export default preview;

import { createTheme, CssBaseline, ThemeProvider } from "@mui/material";
import { configureStore } from "@reduxjs/toolkit";
import { initialize, mswLoader } from "msw-storybook-addon";
import { SnackbarProvider } from "notistack";
import { ErrorBoundary } from "react-error-boundary";
import { Provider } from "react-redux";
import { MemoryRouter, Routes, Route } from "react-router-dom";

import { AppFallback } from "../src/pages/App/AppFallback";
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
      auth: { ...mockAuthedState.auth, ...storyPreloadedState?.auth },
    };

    const store = configureStore({
      reducer: rootReducer,
      preloadedState,
      middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(tcApi.middleware),
    });

    // --- IMPORTANT: Force remount on args change AND viewport change ---
    // RTK Query caches data. When args or viewport change via Storybook's GUI,
    // RTK Query hooks might keep a 'loading' state, freezing the component.
    // Changing the 'key' forces React to remount the entire tree,
    // creating a new, fresh store and clearing all RTK Query cache.
    // This is the simplest way to ensure Storybook's GUI works reliably with RTK Query
    const key = JSON.stringify(context.args) + "-" + context.globals.viewport?.value;

    // Get router parameters from the story
    const { router: routerParameters } = context.parameters;

    return (
      <MemoryRouter {...routerParameters?.memoryRouterProps}>
        <Provider store={store} key={key}>
          <AuthProvider>
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <SnackbarProvider
                maxSnack={3}
                preventDuplicate={true}
                anchorOrigin={{ horizontal: "center", vertical: "top" }}
                autoHideDuration={5000}
              >
                <ErrorBoundary FallbackComponent={AppFallback}>
                  {routerParameters?.useRoutes ? (
                    <Routes>
                      <Route path={routerParameters.path} element={<Story {...context} />} />
                    </Routes>
                  ) : (
                    <Story {...context} />
                  )}
                </ErrorBoundary>
              </SnackbarProvider>
            </ThemeProvider>
          </AuthProvider>
        </Provider>
      </MemoryRouter>
    );
  },
];

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

import { configureStore } from "@reduxjs/toolkit";
import { initialize, mswLoader } from "msw-storybook-addon";
import { Provider } from "react-redux";

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

export const decorators = [
  (Story, context) => {
    const { preloadedState } = context.parameters.redux || {};

    const store = configureStore({
      reducer: rootReducer,
      preloadedState: preloadedState || mockAuthedState,
      middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(tcApi.middleware),
    });

    const key = JSON.stringify(context.args);

    return (
      <Provider key={key} store={store}>
        <Story />
      </Provider>
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

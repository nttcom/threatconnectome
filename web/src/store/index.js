import { configureStore } from "@reduxjs/toolkit";

import { firebaseApi } from "../services/firebaseApi";
import { tcApi } from "../services/tcApi";
import { sliceReducers } from "../slices";

const store = configureStore({
  reducer: {
    ...sliceReducers,
    [tcApi.reducerPath]: tcApi.reducer,
    [firebaseApi.reducerPath]: firebaseApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        /* disable serializableCheck for firebase to avoid error:
         *   A non-serializable value was detected, ...
         * https://redux-toolkit.js.org/usage/usage-guide#working-with-non-serializable-data
         * https://redux-toolkit.js.org/api/serializabilityMiddleware#options
         */
        ignoredActions: [
          "firebaseApi/executeMutation/fulfilled",
          "firebaseApi/executeMutation/pending",
          "firebaseApi/executeMutation/rejected",
        ],
        ignoredPaths: [new RegExp("^firebaseApi.mutations.*")],
      },
    })
      .concat(tcApi.middleware)
      .concat(firebaseApi.middleware),
  devTools: process.env.NODE_ENV !== "production",
});

export default store;

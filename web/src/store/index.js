import { configureStore } from "@reduxjs/toolkit";

import { tcApi } from "../services/tcApi";
import { sliceReducers } from "../slices";

const store = configureStore({
  reducer: {
    ...sliceReducers,
    [tcApi.reducerPath]: tcApi.reducer,
  },
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(tcApi.middleware),
  devTools: import.meta.env.NODE_ENV !== "production",
});

export default store;

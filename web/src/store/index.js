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
    getDefaultMiddleware().concat(tcApi.middleware).concat(firebaseApi.middleware),
});

export default store;

import { createSlice } from "@reduxjs/toolkit";

const _initialState = {
  authUserIsReady: false,
  redirectedFrom: { from: undefined, search: undefined },
};

const authSlice = createSlice({
  name: "auth",
  initialState: _initialState,
  reducers: {
    setAuthUserIsReady: (state, action) => ({
      ...state,
      authUserIsReady: action.payload,
    }),
    setRedirectedFrom: (state, action) => ({
      ...state,
      redirectedFrom: { from: action.payload.from, search: action.payload.search },
    }),
  },
});

const { actions, reducer } = authSlice;

export const { setAuthUserIsReady, setRedirectedFrom } = actions;

export default reducer;

import { createSlice } from "@reduxjs/toolkit";

const _initialState = {
  authUserIsReady: false,
};

const authSlice = createSlice({
  name: "auth",
  initialState: _initialState,
  reducers: {
    setAuthUserIsReady: (state, action) => ({
      ...state,
      authUserIsReady: action.payload,
    }),
  },
});

const { actions, reducer } = authSlice;

export const { setAuthUserIsReady } = actions;

export default reducer;

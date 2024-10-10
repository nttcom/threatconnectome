import { createSlice } from "@reduxjs/toolkit";

const _initialState = {
  token: undefined,
};

const authSlice = createSlice({
  name: "auth",
  initialState: _initialState,
  reducers: {
    clearAuth: (state, action) => ({
      ..._initialState,
    }),
    setAuthToken: (state, action) => ({
      ...state,
      token: action.payload,
    }),
  },
});

const { actions, reducer } = authSlice;

export const { clearAuth, setAuthToken } = actions;

export default reducer;

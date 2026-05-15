import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

export type RedirectedFrom = {
  from: string | undefined;
  search: string | undefined;
};

export type AuthState = {
  authUserIsReady: boolean;
  redirectedFrom: RedirectedFrom;
};

const initialState: AuthState = {
  authUserIsReady: false,
  redirectedFrom: { from: undefined, search: undefined },
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setAuthUserIsReady: (state, action: PayloadAction<boolean>) => ({
      ...state,
      authUserIsReady: action.payload,
    }),
    setRedirectedFrom: (state, action: PayloadAction<{ from?: string; search?: string }>) => ({
      ...state,
      redirectedFrom: { from: action.payload.from, search: action.payload.search },
    }),
  },
});

const { actions, reducer } = authSlice;

export const { setAuthUserIsReady, setRedirectedFrom } = actions;

export default reducer;

import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { getMyUserInfo as apiGetUser } from "../utils/api";

export const getUser = createAsyncThunk(
  "user/get",
  async () => await apiGetUser().then((response) => response.data),
);

const _initialUserState = {
  user: {},
};

const userSlice = createSlice({
  name: "user",
  initialState: _initialUserState,
  reducers: {
    clearUser: (state, action) => ({
      ..._initialUserState,
    }),
  },
  extraReducers: (builder) => {
    builder.addCase(getUser.fulfilled, (state, action) => ({
      ...state,
      user: action.payload,
    }));
  },
});

const { actions, reducer } = userSlice;

export const { clearUser } = actions;

export default reducer;

import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import {
  createUser as apiCreateUser,
  getMyUserInfo as apiGetUser,
  updateUser as apiUpdateUser,
} from "../utils/api";

export const createUser = createAsyncThunk(
  "user/create",
  async (data) => await apiCreateUser(data).then((response) => response.data),
);

export const getUser = createAsyncThunk(
  "user/get",
  async () => await apiGetUser().then((response) => response.data),
);

export const updateUser = createAsyncThunk(
  "user/update",
  async (data) =>
    await apiUpdateUser(data.userId, { ...data.user }).then((response) => response.data),
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
    builder
      .addCase(createUser.fulfilled, (state, action) => ({
        ...state,
        user: action.payload,
      }))
      .addCase(getUser.fulfilled, (state, action) => ({
        ...state,
        user: action.payload,
      }))
      .addCase(updateUser.fulfilled, (state, action) => ({
        ...state,
        user: action.payload,
      }));
  },
});

const { actions, reducer } = userSlice;

export const { clearUser } = actions;

export default reducer;

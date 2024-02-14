import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import {
  createUser as apiCreateUser,
  deleteUser as apiDeleteUser,
  getAchievements as apiGetAchievements,
  getAuthorizedZones as apiGetAuthorizedZones,
  getMyUserInfo as apiGetUser,
  updateUser as apiUpdateUser,
} from "../utils/api";

export const createUser = createAsyncThunk(
  "user/create",
  async (data) => await apiCreateUser(data).then((response) => response.data),
);

export const deleteUser = createAsyncThunk("user/delete", async () => await apiDeleteUser());

export const getAchievements = createAsyncThunk(
  "user/getAchievements",
  async (userId) => await apiGetAchievements(userId).then((response) => response.data),
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

export const getAuthorizedZones = createAsyncThunk(
  "user/getAuthorizedZones",
  async () => await apiGetAuthorizedZones().then((response) => response.data),
);

const _initialUserState = {
  achievements: undefined,
  user: {},
  zones: undefined,
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
      .addCase(getAchievements.fulfilled, (state, action) => ({
        ...state,
        achievements: action.payload,
      }))
      .addCase(createUser.fulfilled, (state, action) => ({
        ...state,
        user: action.payload,
      }))
      .addCase(deleteUser.fulfilled, (state, _action) => ({
        ...state,
        user: {},
      }))
      .addCase(getUser.fulfilled, (state, action) => ({
        ...state,
        user: action.payload,
      }))
      .addCase(updateUser.fulfilled, (state, action) => ({
        ...state,
        user: action.payload,
      }))
      .addCase(getAuthorizedZones.fulfilled, (state, action) => ({
        ...state,
        zones: action.payload,
      }));
  },
});

const { actions, reducer } = userSlice;

export const { clearUser } = actions;

export default reducer;

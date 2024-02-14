import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import {
  getATeam as apiGetATeam,
  getATeamAuth as apiGetATeamAuth,
  getATeamAuthInfo as apiGetATeamAuthInfo,
  getATeamMembers as apiGetATeamMembers,
  getATeamTopics as apiGetATeamTopics,
} from "../utils/api";

export const getATeam = createAsyncThunk(
  "ateam/getATeam",
  async (ateamId) =>
    await apiGetATeam(ateamId).then((response) => ({
      data: response.data,
      ateamId: ateamId,
    })),
);

export const getATeamAuthInfo = createAsyncThunk(
  "ateams/getAuthInfo",
  async () =>
    await apiGetATeamAuthInfo().then((response) => ({
      data: response.data,
    })),
);

export const getATeamAuth = createAsyncThunk(
  "ateam/getATeamAuth",
  async (ateamId) =>
    await apiGetATeamAuth(ateamId).then((response) => ({
      data: response.data,
      ateamId: ateamId,
    })),
);

export const getATeamMembers = createAsyncThunk(
  "ateam/getATeamMembers",
  async (ateamId) =>
    await apiGetATeamMembers(ateamId).then((response) => ({
      data: response.data.reduce(
        (ret, val) => ({
          ...ret,
          [val.user_id]: val,
        }),
        {},
      ),
      ateamId: ateamId,
    })),
);

export const getATeamTopics = createAsyncThunk(
  "ateam/getATeamTopics",
  async (ateamId) =>
    await apiGetATeamTopics(ateamId).then((response) => ({
      data: response.data,
      ateamId: ateamId,
    })),
);

const _initialState = {
  ateamId: undefined,
  ateam: undefined,
  authInfo: undefined,
  authorities: undefined,
  members: undefined,
  ateamTopics: undefined,
};

const ateamSlice = createSlice({
  name: "ateam",
  initialState: _initialState,
  reducers: {
    clearATeam: (state, action) => ({
      ..._initialState,
    }),
    setATeamId: (state, action) => ({
      /*
       * CAUTION: ateam slice is initialized on changing ateamId.
       */
      ...(action.payload && state.ateamId === action.payload ? state : _initialState),
      ateamId: action.payload,
    }),
  },
  extraReducers: (builder) => {
    builder
      .addCase(getATeam.fulfilled, (state, action) => ({
        ...state,
        ateam: action.payload.data,
      }))
      .addCase(getATeamAuthInfo.fulfilled, (state, action) => ({
        ...state,
        authInfo: action.payload.data,
      }))
      .addCase(getATeamAuth.fulfilled, (state, action) => ({
        ...state,
        authorities: action.payload.data,
      }))
      .addCase(getATeamMembers.fulfilled, (state, action) => ({
        ...state,
        members: action.payload.data,
      }))
      .addCase(getATeamTopics.fulfilled, (state, action) => ({
        ...state,
        ateamTopics: action.payload.data,
      }));
  },
});

const { actions, reducer } = ateamSlice;

export const { clearATeam, setATeamId } = actions;

export default reducer;

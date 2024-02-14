import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import {
  getGTeam as apiGetGTeam,
  getGTeamAuth as apiGetGTeamAuth,
  getGTeamAuthInfo as apiGetGTeamAuthInfo,
  getGTeamMembers as apiGetGTeamMembers,
  getGTeamZonesSummary as apiGetGTeamZonesSummary,
} from "../utils/api";

export const getGTeam = createAsyncThunk(
  "gteam/getGTeam",
  async (gteamId) =>
    await apiGetGTeam(gteamId).then((response) => ({
      data: response.data,
      gteamId: gteamId,
    })),
);

export const getGTeamAuthInfo = createAsyncThunk(
  "gteam/getAuthInfo",
  async () =>
    await apiGetGTeamAuthInfo().then((response) => ({
      data: response.data,
    })),
);

export const getGTeamAuth = createAsyncThunk(
  "gteam/getGTeamAuth",
  async (gteamId) =>
    await apiGetGTeamAuth(gteamId).then((response) => ({
      data: response.data,
      gteamId: gteamId,
    })),
);

export const getGTeamMembers = createAsyncThunk(
  "gteam/getGTeamMembers",
  async (gteamId) =>
    await apiGetGTeamMembers(gteamId).then((response) => ({
      data: response.data.reduce(
        (ret, val) => ({
          ...ret,
          [val.user_id]: val,
        }),
        {},
      ),
      gteamId: gteamId,
    })),
);

export const getGTeamZonesSummary = createAsyncThunk(
  "gteam/getGTeamZonesSummary",
  async (gteamId) =>
    await apiGetGTeamZonesSummary(gteamId).then((response) => ({
      data: response.data,
      gteamId: gteamId,
    })),
);

const _initialState = {
  gteamId: undefined,
  gteam: undefined,
  authInfo: undefined,
  authorities: undefined,
  members: undefined,
  zonesSummary: undefined,
};

const gteamSlice = createSlice({
  name: "gteam",
  initialState: _initialState,
  reducers: {
    clearGTeam: (state, action) => ({
      ..._initialState,
    }),
    setGTeamId: (state, action) => ({
      /*
       * CAUTION: gteam slice is initialized on changing gteamId.
       */
      ...(action.payload && state.gteamId === action.payload ? state : _initialState),
      gteamId: action.payload,
    }),
  },
  extraReducers: (builder) => {
    builder
      .addCase(getGTeam.fulfilled, (state, action) => ({
        ...state,
        gteam: action.payload.data,
      }))
      .addCase(getGTeamAuthInfo.fulfilled, (state, action) => ({
        ...state,
        authInfo: action.payload.data,
      }))
      .addCase(getGTeamAuth.fulfilled, (state, action) => ({
        ...state,
        authorities: action.payload.data,
      }))
      .addCase(getGTeamMembers.fulfilled, (state, action) => ({
        ...state,
        members: action.payload.data,
      }))
      .addCase(getGTeamZonesSummary.fulfilled, (state, action) => ({
        ...state,
        zonesSummary: action.payload.data,
      }));
  },
});

const { actions, reducer } = gteamSlice;

export const { clearGTeam, setGTeamId } = actions;

export default reducer;

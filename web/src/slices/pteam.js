import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import {
  getDependencies as apiGetDependencies,
  getPTeamServiceTagsSummary as apiGetPTeamServiceTagsSummary,
  getPTeamTagsSummary as apiGetPTeamTagsSummary,
} from "../utils/api";

export const getDependencies = createAsyncThunk(
  "pteam/getDependencies",
  async (data) =>
    await apiGetDependencies(data.pteamId, data.serviceId).then((response) => ({
      pteamId: data.pteamId,
      serviceId: data.serviceId,
      data: response.data,
    })),
);

export const getPTeamServiceTagsSummary = createAsyncThunk(
  "pteam/getPTeamServiceTagsSummary",
  async (data) =>
    await apiGetPTeamServiceTagsSummary(data.pteamId, data.serviceId).then((response) => ({
      data: response.data,
      pteamId: data.pteamId,
      serviceId: data.serviceId,
    })),
);

export const getPTeamTagsSummary = createAsyncThunk(
  "pteam/getPTeamTagsSummary",
  async (data) =>
    await apiGetPTeamTagsSummary(data.pteamId).then((response) => ({
      data: response.data,
      pteamId: data.pteamId,
    })),
);

const _initialState = {
  pteamId: undefined,
  serviceDependencies: {}, // dict[serviceId: list[dependency]]
  serviceTagsSummaries: {},
  pteamTagsSummaries: {},
  serviceThumbnails: {}, // dict[serviceId: dataURL | noImageAvailableUrl(=NoThumbnail)]
};

const pteamSlice = createSlice({
  name: "pteam",
  initialState: _initialState,
  reducers: {
    clearPTeam: (state, action) => ({
      ..._initialState,
    }),
    setPTeamId: (state, action) => ({
      /*
       * CAUTION: pteam slice is initialized on changing pteamId.
       */
      ...(action.payload && state.pteamId === action.payload ? state : _initialState),
      pteamId: action.payload,
    }),
    invalidateServiceId: (state, action) => ({
      ...state,
      /* Note: state.pteam.services should be fixed by dispatch(getPTeam(pteamId)) */
      serviceDependencies: { ...state.serviceDependencies, [action.payload]: undefined },
      serviceTagsSummaries: { ...state.serviceTagsSummaries, [action.payload]: undefined },
      tickets: { ...state.tickets, [action.payload]: undefined },
      serviceThumbnails: { ...state.serviceThumbnails, [action.payload]: undefined },
    }),
    storeServiceThumbnail: (state, action) => ({
      ...state,
      serviceThumbnails: {
        ...state.serviceThumbnails,
        [action.payload.serviceId]: action.payload.data,
      },
    }),
    storeServiceThumbnailDict: (state, action) => ({
      ...state,
      serviceThumbnails: {
        ...state.serviceThumbnails,
        ...action.payload,
      },
    }),
  },
  extraReducers: (builder) => {
    builder
      .addCase(getDependencies.fulfilled, (state, action) => ({
        ...state,
        serviceDependencies: {
          ...state.serviceDependencies,
          [action.payload.serviceId]: action.payload.data,
        },
      }))
      .addCase(getPTeamServiceTagsSummary.fulfilled, (state, action) => ({
        ...state,
        serviceTagsSummaries: {
          ...state.serviceTagsSummaries,
          [action.payload.serviceId]: action.payload.data,
        },
      }))
      .addCase(getPTeamTagsSummary.fulfilled, (state, action) => ({
        ...state,
        pteamTagsSummaries: {
          ...state.pteamTagsSummaries,
          [action.payload.pteamId]: action.payload.data,
        },
      }));
  },
});

const { actions, reducer } = pteamSlice;

export const {
  clearPTeam,
  setPTeamId,
  invalidateServiceId,
  storeServiceThumbnail,
  storeServiceThumbnailDict,
} = actions;

export default reducer;

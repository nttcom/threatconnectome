import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import {
  getDependencies as apiGetDependencies,
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
    invalidateServiceId: (state, action) => ({
      ...state,
      /* Note: state.pteam.services should be fixed by dispatch(getPTeam(pteamId)) */
      serviceDependencies: { ...state.serviceDependencies, [action.payload]: undefined },
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

export const { clearPTeam, invalidateServiceId, storeServiceThumbnail, storeServiceThumbnailDict } =
  actions;

export default reducer;

import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { getPTeamTagsSummary as apiGetPTeamTagsSummary } from "../utils/api";

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
    builder.addCase(getPTeamTagsSummary.fulfilled, (state, action) => ({
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

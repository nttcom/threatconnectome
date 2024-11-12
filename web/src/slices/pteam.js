import { createSlice } from "@reduxjs/toolkit";

const _initialState = {
  pteamId: undefined,
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
});

const { actions, reducer } = pteamSlice;

export const { clearPTeam, invalidateServiceId, storeServiceThumbnail, storeServiceThumbnailDict } =
  actions;

export default reducer;

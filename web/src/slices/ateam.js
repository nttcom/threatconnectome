import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { getATeam as apiGetATeam, getATeamTopics as apiGetATeamTopics } from "../utils/api";

export const getATeam = createAsyncThunk(
  "ateam/getATeam",
  async (ateamId) =>
    await apiGetATeam(ateamId).then((response) => ({
      data: response.data,
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
  ateamTopics: undefined,
};

const ateamSlice = createSlice({
  name: "ateam",
  initialState: _initialState,
  reducers: {
    clearATeam: (state, action) => ({
      ..._initialState,
    }),
  },
  extraReducers: (builder) => {
    builder
      .addCase(getATeam.fulfilled, (state, action) => ({
        ...state,
        ateam: action.payload.data,
      }))
      .addCase(getATeamTopics.fulfilled, (state, action) => ({
        ...state,
        ateamTopics: action.payload.data,
      }));
  },
});

const { actions, reducer } = ateamSlice;

export const { clearATeam } = actions;

export default reducer;

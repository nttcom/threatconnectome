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
      .addCase(getATeamTopics.fulfilled, (state, action) => ({
        ...state,
        ateamTopics: action.payload.data,
      }));
  },
});

const { actions, reducer } = ateamSlice;

export const { clearATeam, setATeamId } = actions;

export default reducer;

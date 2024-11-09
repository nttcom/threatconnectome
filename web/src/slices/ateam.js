import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { getATeam as apiGetATeam } from "../utils/api";

export const getATeam = createAsyncThunk(
  "ateam/getATeam",
  async (ateamId) =>
    await apiGetATeam(ateamId).then((response) => ({
      data: response.data,
      ateamId: ateamId,
    })),
);

const _initialState = {
  ateamId: undefined,
  ateam: undefined,
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
    builder.addCase(getATeam.fulfilled, (state, action) => ({
      ...state,
      ateam: action.payload.data,
    }));
  },
});

const { actions, reducer } = ateamSlice;

export const { clearATeam, setATeamId } = actions;

export default reducer;

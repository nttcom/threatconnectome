import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

const _initialState = {
  ateamId: undefined,
};

const ateamSlice = createSlice({
  name: "ateam",
  initialState: _initialState,
  reducers: {
    clearATeam: (state, action) => ({
      ..._initialState,
    }),
  },
});

const { actions, reducer } = ateamSlice;

export const { clearATeam } = actions;

export default reducer;

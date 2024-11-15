import { createSlice } from "@reduxjs/toolkit";

const systemSlice = createSlice({
  name: "system",
  initialState: {
    drawerOpen: true,
  },
  reducers: {
    setDrawerOpen: (state, action) => ({
      ...state,
      drawerOpen: action.payload,
    }),
  },
});

const { actions, reducer } = systemSlice;

export const { setDrawerOpen } = actions;

export default reducer;

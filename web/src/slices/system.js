import { createSlice } from "@reduxjs/toolkit";

const systemSlice = createSlice({
  name: "system",
  initialState: {
    drawerOpen: true,
    teamMode: "pteam", // "pteam" or "ateam"
  },
  reducers: {
    setDrawerOpen: (state, action) => ({
      ...state,
      drawerOpen: action.payload,
    }),
    setTeamMode: (state, action) => ({
      ...state,
      teamMode: action.payload,
    }),
  },
});

const { actions, reducer } = systemSlice;

export const { setDrawerOpen, setTeamMode } = actions;

export default reducer;

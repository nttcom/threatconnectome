import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

export type SystemState = {
  drawerOpen: boolean;
};

const initialState: SystemState = {
  drawerOpen: false,
};

const systemSlice = createSlice({
  name: "system",
  initialState,
  reducers: {
    setDrawerOpen: (state, action: PayloadAction<boolean>) => ({
      ...state,
      drawerOpen: action.payload,
    }),
  },
});

const { actions, reducer } = systemSlice;

export const { setDrawerOpen } = actions;

export default reducer;

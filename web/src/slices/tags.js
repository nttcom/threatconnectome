import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { getTags as apiGetTags } from "../utils/api";

export const getTags = createAsyncThunk("tags/get", async () => {
  return await apiGetTags().then((response) => response.data);
});

const _initialState = {
  allTags: undefined,
};

const tagsSlice = createSlice({
  name: "tags",
  initialState: _initialState,
  extraReducers: (builder) => {
    builder.addCase(getTags.fulfilled, (state, action) => ({
      ...state,
      allTags: action.payload, // payload is already sorted by tag_name
    }));
  },
});

const { reducer } = tagsSlice;

export default reducer;

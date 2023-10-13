import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { getTopic as apiGetTopic } from "../utils/api";

export const getTopic = createAsyncThunk(
  "topics/get",
  async (topicId) => await apiGetTopic(topicId).then((response) => response.data)
);

const topicsSlice = createSlice({
  name: "topics",
  initialState: {},
  extraReducers: (builder) => {
    builder.addCase(getTopic.fulfilled, (state, action) => ({
      ...state,
      [action.payload.topic_id]: {
        ...action.payload,
      },
    }));
  },
});

const { reducer } = topicsSlice;

export default reducer;

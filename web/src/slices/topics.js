import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { getTopic as apiGetTopic } from "../utils/api";

export const getTopic = createAsyncThunk(
  "topics/get",
  async (topicId) => await apiGetTopic(topicId).then((response) => response.data),
);

const _initialState = {
  topics: {}, // {topicId: TopicResponse}
};

const topicsSlice = createSlice({
  name: "topics",
  initialState: _initialState,
  reducers: {
    clearTopics: (state, action) => ({
      /* Note: at least, actions should be cleared with topics. */
      ..._initialState,
    }),
  },
  extraReducers: (builder) => {
    builder.addCase(getTopic.fulfilled, (state, action) => ({
      ...state,
      topics: {
        ...state.topics,
        [action.payload.topic_id]: action.payload,
      },
    }));
  },
});

const { actions, reducer } = topicsSlice;

export const { clearTopics } = actions;

export default reducer;

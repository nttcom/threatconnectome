import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import {
  getTopic as apiGetTopic,
  getUserTopicActions as apiGetUserTopicActions,
} from "../utils/api";

export const getTopic = createAsyncThunk(
  "topics/get",
  async (topicId) => await apiGetTopic(topicId).then((response) => response.data)
);

export const getActions = createAsyncThunk(
  "topics/getActions",
  async (topicId) =>
    await apiGetUserTopicActions(topicId).then((response) => ({
      data: response.data,
      topicId: topicId,
    }))
);

const _initialState = {
  topics: {}, // {topicId: TopicResponse}
  actions: {}, // {topicId: List[ActionResponse]}
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
    builder
      .addCase(getTopic.fulfilled, (state, action) => ({
        ...state,
        topics: {
          ...state.topics,
          [action.payload.topic_id]: action.payload,
        },
      }))
      .addCase(getActions.fulfilled, (state, action) => ({
        ...state,
        actions: {
          ...state.actions,
          [action.payload.topicId]: action.payload.data,
        },
      }));
  },
});

const { actions, reducer } = topicsSlice;

export const { clearTopics } = actions;

export default reducer;

import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import {
  getPTeam as apiGetPTeam,
  getPTeamAchievements as apiGetPTeamAchievements,
  getPTeamAuth as apiGetPTeamAuth,
  getPTeamAuthInfo as apiGetPTeamAuthInfo,
  getPTeamMembers as apiGetPTeamMembers,
  getPTeamSolvedTaggedTopicIds as apiGetPTeamSolvedTaggedTopicIds,
  getPTeamUnsolvedTaggedTopicIds as apiGetPTeamUnsolvedTaggedTopicIds,
  getPTeamTag as apiGetPTeamTag,
  getPTeamTagsSummary as apiGetPTeamTagsSummary,
  getPTeamTopicActions as apiGetPTeamTopicActions,
  getPTeamTopicStatus as apiGetPTeamTopicStatus,
  getPTeamTopicStatusesSummary as apiGetPTeamTopicStatusesSummary,
  getPTeamWatcher as apiGetPTeamWatcher,
  getPTeamGroups as apiGetPTeamGroups,
} from "../utils/api";

export const getPTeam = createAsyncThunk(
  "pteam/getPTeam",
  async (pteamId) =>
    await apiGetPTeam(pteamId).then((response) => ({
      data: response.data,
      pteamId: pteamId,
    }))
);

export const getPTeamAchievements = createAsyncThunk(
  "pteam/getPTeamAchievements",
  async (pteamId) =>
    await apiGetPTeamAchievements(pteamId).then((response) => ({
      data: response.data,
      pteamId: pteamId,
    }))
);

export const getPTeamAuthInfo = createAsyncThunk(
  "pteams/getAuthInfo",
  async () =>
    await apiGetPTeamAuthInfo().then((response) => ({
      data: response.data,
    }))
);

export const getPTeamAuth = createAsyncThunk(
  "pteam/getPTeamAuth",
  async (pteamId) =>
    await apiGetPTeamAuth(pteamId).then((response) => ({
      data: response.data,
      pteamId: pteamId,
    }))
);

export const getPTeamMembers = createAsyncThunk(
  "pteam/getPTeamMembers",
  async (pteamId) =>
    await apiGetPTeamMembers(pteamId).then((response) => ({
      data: response.data.reduce(
        (ret, val) => ({
          ...ret,
          [val.user_id]: val,
        }),
        {}
      ),
      pteamId: pteamId,
    }))
);

export const getPTeamTag = createAsyncThunk(
  "pteam/getPTeamTag",
  async (data) =>
    await apiGetPTeamTag(data.pteamId, data.tagId)
      .then((response) => ({
        pteamId: data.pteamId,
        tagId: data.tagId,
        data: response.data,
      }))
      .catch((error) => {
        if (data.onError) data.onError(error);
        throw error;
      })
);

export const getPTeamSolvedTaggedTopicIds = createAsyncThunk(
  "pteam/getPTeamSolvedTaggedTopicIds",
  async (data) =>
    await apiGetPTeamSolvedTaggedTopicIds(data.pteamId, data.tagId).then((response) => ({
      pteamId: data.pteamId,
      tagId: data.tagId,
      data: response.data,
    }))
);

export const getPTeamUnsolvedTaggedTopicIds = createAsyncThunk(
  "pteam/getPTeamUnsolvedTaggedTopicIds",
  async (data) =>
    await apiGetPTeamUnsolvedTaggedTopicIds(data.pteamId, data.tagId).then((response) => ({
      pteamId: data.pteamId,
      tagId: data.tagId,
      data: response.data,
    }))
);

export const getPTeamTagsSummary = createAsyncThunk(
  "pteam/getPTeamTagsSummary",
  async (pteamId) =>
    await apiGetPTeamTagsSummary(pteamId).then((response) => ({
      data: response.data,
      pteamId: pteamId,
    }))
);

export const getPTeamTopicStatusesSummary = createAsyncThunk(
  "pteam/getPTeamTopicStatusesSummary",
  async (data) =>
    await apiGetPTeamTopicStatusesSummary(data.pteamId, data.tagId).then((response) => ({
      data: response.data,
      pteamId: data.pteamId,
      tagId: data.tagId,
    }))
);

export const getPTeamTopicStatus = createAsyncThunk(
  "pteam/getPTeamTopicStatus",
  async (data) =>
    await apiGetPTeamTopicStatus(data.pteamId, data.topicId, data.tagId).then((response) => ({
      data: response.data || {},
      pteamId: data.pteamId,
      topicId: data.topicId,
      tagId: data.tagId,
    }))
);

export const getPTeamTopicActions = createAsyncThunk(
  "pteam/getPTeamTopicActions",
  async (data) =>
    await apiGetPTeamTopicActions(data.pteamId, data.topicId).then((response) => ({
      actions: response.data.actions,
      pteamId: data.pteamId,
      topicId: data.topicId,
    }))
);

export const getPTeamWatcher = createAsyncThunk(
  "pteam/getPTeamWatcher",
  async (pteamId) =>
    await apiGetPTeamWatcher(pteamId).then((response) => ({
      data: response.data,
      pteamId: pteamId,
    }))
);

export const getPTeamGroups = createAsyncThunk(
  "pteam/getPTeamGroups",
  async (pteamId) =>
    await apiGetPTeamGroups(pteamId).then((response) => ({
      groups: response.data.groups,
      pteamId: pteamId,
    }))
);

const _initialState = {
  pteamId: undefined,
  pteam: undefined,
  achievements: undefined,
  authInfo: undefined,
  authorities: undefined,
  members: undefined,
  tagsSummary: undefined,
  topicsSummary: undefined,
  pteamtags: {},
  taggedTopics: {},
  topicStatus: {},
  topicActions: {},
  groups: undefined,
};

const pteamSlice = createSlice({
  name: "pteam",
  initialState: _initialState,
  reducers: {
    clearPTeam: (state, action) => ({
      ..._initialState,
    }),
    setPTeamId: (state, action) => ({
      /*
       * CAUTION: pteam slice is initialized on changing pteamId.
       */
      ...(action.payload && state.pteamId === action.payload ? state : _initialState),
      pteamId: action.payload,
    }),
  },
  extraReducers: (builder) => {
    builder
      .addCase(getPTeam.fulfilled, (state, action) => ({
        ...state,
        pteam: action.payload.data,
      }))
      .addCase(getPTeamAchievements.fulfilled, (state, action) => ({
        ...state,
        achievements: action.payload.data,
      }))
      .addCase(getPTeamAuthInfo.fulfilled, (state, action) => ({
        ...state,
        authInfo: action.payload.data,
      }))
      .addCase(getPTeamAuth.fulfilled, (state, action) => ({
        ...state,
        authorities: action.payload.data,
      }))
      .addCase(getPTeamMembers.fulfilled, (state, action) => ({
        ...state,
        members: action.payload.data,
      }))
      .addCase(getPTeamTagsSummary.fulfilled, (state, action) => ({
        ...state,
        tagsSummary: action.payload.data,
      }))
      .addCase(getPTeamTopicStatusesSummary.fulfilled, (state, action) => ({
        ...state,
        topicsSummary: action.payload.data,
      }))
      .addCase(getPTeamTag.fulfilled, (state, action) => ({
        ...state,
        pteamtags: {
          ...state.pteamtags,
          [action.payload.tagId]: action.payload.data,
        },
      }))
      .addCase(getPTeamSolvedTaggedTopicIds.fulfilled, (state, action) => ({
        ...state,
        taggedTopics: {
          ...state.taggedTopics,
          [action.payload.tagId]: {
            ...state.taggedTopics[action.payload.tagId],
            solved: action.payload.data,
          },
        },
      }))
      .addCase(getPTeamUnsolvedTaggedTopicIds.fulfilled, (state, action) => ({
        ...state,
        taggedTopics: {
          ...state.taggedTopics,
          [action.payload.tagId]: {
            ...state.taggedTopics[action.payload.tagId],
            unsolved: action.payload.data,
          },
        },
      }))
      .addCase(getPTeamTopicStatus.fulfilled, (state, action) => ({
        ...state,
        topicStatus: {
          ...state.topicStatus,
          [action.payload.topicId]: {
            ...state.topicStatus[action.payload.topicId],
            [action.payload.tagId]: action.payload.data,
          },
        },
      }))
      .addCase(getPTeamTopicActions.fulfilled, (state, action) => ({
        ...state,
        topicActions: {
          ...state.topicActions,
          [action.payload.topicId]: action.payload.actions,
        },
      }))
      .addCase(getPTeamGroups.fulfilled, (state, action) => ({
        ...state,
        groups: action.payload.groups,
      }));
  },
});

const { actions, reducer } = pteamSlice;

export const { clearPTeam, setPTeamId } = actions;

export default reducer;

import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import {
  getDependencies as apiGetDependencies,
  getPTeam as apiGetPTeam,
  getPTeamAuth as apiGetPTeamAuth,
  getPTeamAuthInfo as apiGetPTeamAuthInfo,
  getPTeamMembers as apiGetPTeamMembers,
  getPTeamServiceTaggedTicketIds as apiGetPTeamServiceTaggedTicketIds,
  getPTeamTopicActions as apiGetPTeamTopicActions,
  getTopicStatus as apiGetTopicStatus,
  getPTeamServiceTagsSummary as apiGetPTeamServiceTagsSummary,
} from "../utils/api";

export const getPTeam = createAsyncThunk(
  "pteam/getPTeam",
  async (pteamId) =>
    await apiGetPTeam(pteamId).then((response) => ({
      data: response.data,
      pteamId: pteamId,
    })),
);

export const getPTeamAuthInfo = createAsyncThunk(
  "pteams/getAuthInfo",
  async () =>
    await apiGetPTeamAuthInfo().then((response) => ({
      data: response.data,
    })),
);

export const getPTeamAuth = createAsyncThunk(
  "pteam/getPTeamAuth",
  async (pteamId) =>
    await apiGetPTeamAuth(pteamId).then((response) => ({
      data: response.data,
      pteamId: pteamId,
    })),
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
        {},
      ),
      pteamId: pteamId,
    })),
);

export const getDependencies = createAsyncThunk(
  "pteam/getDependencies",
  async (data) =>
    await apiGetDependencies(data.pteamId, data.serviceId).then((response) => ({
      pteamId: data.pteamId,
      serviceId: data.serviceId,
      data: response.data,
    })),
);

export const getPTeamServiceTaggedTicketIds = createAsyncThunk(
  "pteam/getPTeamServiceTaggedTicketIds",
  async (data) =>
    await apiGetPTeamServiceTaggedTicketIds(data.pteamId, data.serviceId, data.tagId).then(
      (response) => ({
        pteamId: data.pteamId,
        serviceId: data.serviceId,
        tagId: data.tagId,
        data: response.data,
      }),
    ),
);

export const getTopicStatus = createAsyncThunk(
  "pteam/getTopicStatus",
  async (data) =>
    await apiGetTopicStatus(data.pteamId, data.serviceId, data.topicId, data.tagId).then(
      (response) => ({
        data: response.data || {},
        pteamId: data.pteamId,
        serviceId: data.serviceId,
        topicId: data.topicId,
        tagId: data.tagId,
      }),
    ),
);

export const getPTeamTopicActions = createAsyncThunk(
  "pteam/getPTeamTopicActions",
  async (data) =>
    await apiGetPTeamTopicActions(data.pteamId, data.topicId).then((response) => ({
      actions: response.data.actions,
      pteamId: data.pteamId,
      topicId: data.topicId,
    })),
);

export const getPTeamServiceTagsSummary = createAsyncThunk(
  "pteam/getPTeamServiceTagsSummary",
  async (data) =>
    await apiGetPTeamServiceTagsSummary(data.pteamId, data.serviceId).then((response) => ({
      data: response.data,
      pteamId: data.pteamId,
      serviceId: data.serviceId,
    })),
);

const _initialState = {
  pteamId: undefined,
  pteam: undefined,
  authInfo: undefined,
  authorities: undefined,
  members: undefined,
  serviceDependencies: {}, // dict[serviceId: list[dependency]]
  taggedTopics: {},
  topicStatus: {},
  topicActions: {},
  serviceTagsSummaries: {},
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
    invalidateServiceId: (state, action) => ({
      ...state,
      /* Note: state.pteam.services should be fixed by dispatch(getPTeam(pteamId)) */
      serviceDependencies: { ...state.serviceDependencies, [action.payload]: undefined },
      topicStatus: { ...state.topicStatus, [action.payload]: undefined },
      serviceTagsSummaries: { ...state.serviceTagsSummaries, [action.payload]: undefined },
    }),
  },
  extraReducers: (builder) => {
    builder
      .addCase(getPTeam.fulfilled, (state, action) => ({
        ...state,
        pteam: action.payload.data,
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
      .addCase(getDependencies.fulfilled, (state, action) => ({
        ...state,
        serviceDependencies: {
          ...state.serviceDependencies,
          [action.payload.serviceId]: action.payload.data,
        },
      }))
      .addCase(getPTeamServiceTaggedTicketIds.fulfilled, (state, action) => ({
        ...state,
        taggedTopics: {
          ...state.taggedTopics,
          [action.payload.tagId]: {
            ...state.taggedTopics[action.payload.tagId],
            solved: action.payload.data.solved,
            unsolved: action.payload.data.unsolved,
          },
        },
      }))
      .addCase(getTopicStatus.fulfilled, (state, action) => ({
        ...state,
        topicStatus: {
          ...state.topicStatus,
          [action.payload.serviceId]: {
            ...state.topicStatus[action.payload.serviceId],
            [action.payload.topicId]: {
              ...state.topicStatus[action.payload.topicId],
              [action.payload.tagId]: action.payload.data,
            },
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
      .addCase(getPTeamServiceTagsSummary.fulfilled, (state, action) => ({
        ...state,
        serviceTagsSummaries: {
          ...state.serviceTagsSummaries,
          [action.payload.serviceId]: action.payload.data,
        },
      }));
  },
});

const { actions, reducer } = pteamSlice;

export const { clearPTeam, setPTeamId, invalidateServiceId } = actions;

export default reducer;

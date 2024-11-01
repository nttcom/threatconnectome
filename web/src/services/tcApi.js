import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import { blobToDataURL } from "../utils/func";

const _responseListToDictConverter =
  (keyName, valueName = undefined) =>
  (data, meta, arg) => {
    return data.reduce((ret, item) => {
      /* convert array to dict,
       *    [{x: a, y: b}, ...] => {a: {x: a, y: b}, ...} // if keyName = "x"
       * or [{x: a, y: b}, ...] => {a: b, ...} // and if valueName = "y"
       */
      const key = item[keyName];
      const value = valueName ? item[valueName] : item;
      return {
        ...ret,
        [key]: value,
      };
    }, {});
  };

export const tcApi = createApi({
  reducerPath: "tcApi",
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.REACT_APP_API_BASE_URL,
    prepareHeaders: (headers, { getState }) => {
      /* Note: access token is stored in auth.token via firebaseApi or cookie */
      const token = getState().auth.token;
      if (token) {
        headers.set("authorization", `Bearer ${token}`);
      }
      return headers;
    },
    paramsSerializer: (params) =>
      Object.keys(params)
        .filter((key) => ![null, undefined].includes(params[key]))
        .flatMap((key) =>
          params[key] instanceof Array
            ? params[key].map((item) => `${encodeURIComponent(key)}=${encodeURIComponent(item)}`)
            : `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`,
        )
        .join("&"),
  }),
  endpoints: (builder) => ({
    /* Actions */
    createAction: builder.mutation({
      query: (data) => ({
        url: "/actions",
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "TopicAction", id: "ALL" }],
    }),
    updateAction: builder.mutation({
      query: ({ actionId, data }) => ({
        url: `/actions/${actionId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "TopicAction", id: arg.actionId }],
    }),
    deleteAction: builder.mutation({
      query: (actionId) => ({
        url: `/actions/${actionId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, arg) => [{ type: "TopicAction", id: arg.actionId }],
    }),

    /* Action Log */
    createActionLog: builder.mutation({
      query: (data) => ({
        url: "actionlogs",
        method: "POST",
        body: data,
      }),
    }),

    /* ATeam */
    createATeam: builder.mutation({
      query: (data) => ({
        url: "/ateams",
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "ATeamAccount", id: "ALL" }],
    }),
    updateATeam: builder.mutation({
      query: ({ ateamId, data }) => ({
        url: `/ateams/${ateamId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "ATeam", id: "ALL" }],
    }),

    /* ATeam Auth */
    updateATeamAuth: builder.mutation({
      query: ({ ateamId, data }) => ({
        url: `ateams/${ateamId}/authority`,
        method: "POST",
        body: data,
      }),
    }),

    /* ATeam Invitation */
    createATeamInvitation: builder.mutation({
      query: ({ ateamId, data }) => ({
        url: `ateams/${ateamId}/invitation`,
        method: "POST",
        body: data,
      }),
    }),
    applyATeamInvitation: builder.mutation({
      query: (data) => ({
        url: "ateams/apply_invitation",
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "ATeamAccount", id: "ALL" }],
    }),

    /* ATeam Members */
    getATeamMembers: builder.query({
      query: (ateamId) => ({
        url: `/ateams/${ateamId}/members`,
        method: "GET",
      }),
      providesTags: (result, error, arg) => [
        ...(result
          ? Object.keys(result).reduce(
              (ret, userId) => [...ret, { type: "Account", id: userId }],
              [],
            )
          : []),
        { type: "ATeam", id: "ALL" },
        { type: "ATeamAccount", id: "ALL" },
        { type: "PTeam", id: "ALL" },
        { type: "PTeamAccount", id: "ALL" },
      ],
      transformResponse: _responseListToDictConverter("user_id"),
    }),

    deleteATeamMember: builder.mutation({
      query: ({ ateamId, userId }) => ({
        url: `ateams/${ateamId}/members/${userId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, arg) => [{ type: "ATeamAccount", id: "ALL" }],
    }),

    /* ATeam Watching Request */
    createATeamWatchingRequest: builder.mutation({
      query: ({ ateamId, date }) => ({
        url: `/ateams/${ateamId}/watching_request`,
        method: "POST",
        body: date,
      }),
    }),
    applyATeamWatchingRequest: builder.mutation({
      query: (data) => ({
        url: "/ateams/apply_watching_request",
        method: "POST",
        body: data,
      }),
    }),
    removeWatchingPTeam: builder.mutation({
      query: ({ ateamId, pteamId }) => ({
        url: `/ateams/${ateamId}/watching_pteams/${pteamId}`,
        method: "DELETE",
      }),
    }),

    /* PTeam */
    getPTeam: builder.query({
      query: (pteamId) => `pteams/${pteamId}`,
    }),
    createPTeam: builder.mutation({
      query: (data) => ({
        url: "/pteams",
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "PTeamAccount", id: "ALL" }],
    }),
    updatePTeam: builder.mutation({
      query: ({ pteamId, data }) => ({
        url: `/pteams/${pteamId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "PTeam", id: "ALL" }],
    }),

    /* PTeam Auth Info */
    getPTeamAuthInfo: builder.query({
      query: () => "pteams/auth_info",
    }),

    /* PTeam Auth */
    getPTeamAuth: builder.query({
      query: (pteamId) => `pteams/${pteamId}/authority`,
      transformResponse: _responseListToDictConverter("user_id", "authorities"),
      providesTags: (result, error, pteamId) => [{ type: "PTeamAuth", id: pteamId }],
    }),
    updatePTeamAuth: builder.mutation({
      query: ({ pteamId, data }) => ({
        url: `pteams/${pteamId}/authority`,
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "PTeamAuth", id: arg.pteamId }],
    }),

    /* PTeam Invitation */
    createPTeamInvitation: builder.mutation({
      query: ({ pteamId, data }) => ({
        url: `pteams/${pteamId}/invitation`,
        method: "POST",
        body: data,
      }),
    }),
    applyPTeamInvitation: builder.mutation({
      query: (data) => ({
        url: "pteams/apply_invitation",
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "PTeamAccount", id: "ALL" }],
    }),

    /* PTeam Members */
    getPTeamMembers: builder.query({
      query: (pteamId) => `pteams/${pteamId}/members`,
      transformResponse: _responseListToDictConverter("user_id"),
    }),
    deletePTeamMember: builder.mutation({
      query: ({ pteamId, userId }) => ({
        url: `pteams/${pteamId}/members/${userId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, arg) => [{ type: "PTeamAccount", id: "ALL" }],
    }),

    /* PTeam Service */
    updatePTeamService: builder.mutation({
      query: ({ pteamId, serviceId, data }) => ({
        url: `pteams/${pteamId}/services/${serviceId}`,
        method: "PUT",
        body: data,
      }),
    }),
    deletePTeamService: builder.mutation({
      query: ({ pteamId, serviceName }) => ({
        url: `/pteams/${pteamId}/tags`,
        params: { service: serviceName },
        method: "DELETE",
      }),
    }),

    /* PTeam Service Thumbnail */
    getPTeamServiceThumbnail: builder.query({
      query: ({ pteamId, serviceId }) => ({
        url: `pteams/${pteamId}/services/${serviceId}/thumbnail`,
        responseHandler: async (response) => await blobToDataURL(await response.blob()),
      }),
    }),

    /* PTeam Watchers */
    removeWatcherATeam: builder.mutation({
      query: ({ pteamId, ateamId }) => ({
        url: `/pteams/${pteamId}/watchers/${ateamId}`,
        method: "DELETE",
      }),
    }),

    /* SBOM */
    uploadSBOMFile: builder.mutation({
      query: ({ pteamId, serviceName, sbomFile, forceMode = true }) => {
        const sbomFormData = new FormData();
        sbomFormData.append("file", sbomFile);
        return {
          url: `pteams/${pteamId}/upload_sbom_file`,
          params: { service: serviceName, force_mode: forceMode },
          method: "POST",
          body: sbomFormData,
          /* Note: Content-Type is fixed to multipart/form-data automatically. */
        };
      },
    }),

    /* Ticket Status */
    createTicketStatus: builder.mutation({
      query: ({ pteamId, serviceId, ticketId, data }) => ({
        url: `pteams/${pteamId}/services/${serviceId}/ticketstatus/${ticketId}`,
        method: "POST",
        body: data,
      }),
    }),

    /* TopicAction */
    getPTeamTopicActions: builder.query({
      query: ({ topicId, pteamId }) => ({
        url: `/topics/${topicId}/actions/pteam/${pteamId}`,
        method: "GET",
      }),
      providesTags: (result, error, arg) => [
        ...(result?.actions.reduce(
          (ret, action) => [...ret, { type: "TopicAction", id: action.action_id }],
          [],
        ) ?? []),
        { type: "TopicAction", id: "ALL" },
      ],
    }),

    /* Topic Comment */
    createATeamTopicComment: builder.mutation({
      query: ({ ateamId, topicId, data }) => ({
        url: `ateams/${ateamId}/topiccomment/${topicId}`,
        method: "POST",
        body: data,
      }),
    }),

    updateATeamTopicComment: builder.mutation({
      query: ({ ateamId, topicId, commentId, data }) => ({
        url: `ateams/${ateamId}/topiccomment/${topicId}/${commentId}`,
        method: "PUT",
        body: data,
      }),
    }),

    deleteATeamTopicComment: builder.mutation({
      query: ({ ateamId, topicId, commentId }) => ({
        url: `ateams/${ateamId}/topiccomment/${topicId}/${commentId}`,
        method: "DELETE",
      }),
    }),

    /* Topics */
    searchTopics: builder.query({
      query: (params) => ({
        url: "topics/search",
        params: params,
      }),
    }),
    createTopic: builder.mutation({
      query: ({ topicId, data }) => ({
        url: `/topics/${topicId}`,
        method: "POST",
        body: data,
      }),
    }),

    updateTopic: builder.mutation({
      query: ({ topicId, data }) => ({
        url: `topics/${topicId}`,
        method: "PUT",
        body: data,
      }),
    }),

    deleteTopic: builder.mutation({
      query: (topicId) => ({
        url: `topics/${topicId}`,
        method: "DELETE",
      }),
    }),

    /* User */
    createUser: builder.mutation({
      query: (data) => ({
        url: "/users",
        method: "POST",
        body: data,
      }),
    }),
    updateUser: builder.mutation({
      query: ({ userId, data }) => ({
        url: `/users/${userId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "Account", id: arg.userId }],
    }),
    /* tags */
    createTag: builder.mutation({
      query: (data) => ({
        url: "/tags",
        method: "POST",
        body: data,
      }),
    }),
    /* External */
    checkMail: builder.mutation({
      query: (data) => ({
        url: "external/email/check",
        method: "POST",
        body: data,
      }),
    }),
    checkSlack: builder.mutation({
      query: (data) => ({
        url: "external/slack/check",
        method: "POST",
        body: data,
      }),
    }),
  }),
});

export const {
  useCreateActionMutation,
  useUpdateActionMutation,
  useDeleteActionMutation,
  useCreateActionLogMutation,
  useCreateATeamMutation,
  useUpdateATeamMutation,
  useUpdateATeamAuthMutation,
  useCreateATeamInvitationMutation,
  useApplyATeamInvitationMutation,
  useGetATeamMembersQuery,
  useGetPTeamTopicActionsQuery,
  useDeleteATeamMemberMutation,
  useDeleteATeamTopicCommentMutation,
  useCreateATeamTopicCommentMutation,
  useCreateATeamWatchingRequestMutation,
  useApplyATeamWatchingRequestMutation,
  useRemoveWatchingPTeamMutation,
  useGetPTeamQuery,
  useCreatePTeamMutation,
  useUpdateATeamTopicCommentMutation,
  useUpdatePTeamMutation,
  useUpdatePTeamAuthMutation,
  useUpdateTopicMutation,
  useGetPTeamAuthInfoQuery,
  useGetPTeamAuthQuery,
  useCreatePTeamInvitationMutation,
  useApplyPTeamInvitationMutation,
  useGetPTeamMembersQuery,
  useDeletePTeamMemberMutation,
  useDeleteTopicMutation,
  useUploadSBOMFileMutation,
  useUpdatePTeamServiceMutation,
  useDeletePTeamServiceMutation,
  useGetPTeamServiceThumbnailQuery,
  useRemoveWatcherATeamMutation,
  useCreateTicketStatusMutation,
  useSearchTopicsQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useCreateTopicMutation,
  useCreateTagMutation,
  useCheckMailMutation,
  useCheckSlackMutation,
} = tcApi;

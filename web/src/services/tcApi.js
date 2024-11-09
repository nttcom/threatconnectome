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
        url: "actions",
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "TopicAction", id: "ALL" },
        { type: "Ticket", id: "ALL" },
      ],
    }),
    updateAction: builder.mutation({
      query: ({ actionId, data }) => ({
        url: `actions/${actionId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "TopicAction", id: arg.actionId }],
    }),
    deleteAction: builder.mutation({
      query: (actionId) => ({
        url: `actions/${actionId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "TopicAction", id: arg.actionId },
        { type: "Ticket", id: "ALL" },
      ],
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
        url: "ateams",
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "ATeamAccount", id: "ALL" }],
    }),
    updateATeam: builder.mutation({
      query: ({ ateamId, data }) => ({
        url: `ateams/${ateamId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "ATeam", id: arg.ateamId },
        { type: "ATeam", id: "ALL" },
      ],
    }),

    /* ATeam Auth Info */
    getATeamAuthInfo: builder.query({
      query: () => "ateams/auth_info",
      /* No tags to provide */
    }),

    /* ATeam Auth */
    getATeamAuth: builder.query({
      query: (ateamId) => `ateams/${ateamId}/authority`,
      transformResponse: _responseListToDictConverter("user_id", "authorities"),
      providesTags: (result, error, ateamId) => [{ type: "ATeamAuthority", id: ateamId }],
    }),
    updateATeamAuth: builder.mutation({
      query: ({ ateamId, data }) => ({
        url: `ateams/${ateamId}/authority`,
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "ATeamAuthority", id: arg.ateamId }],
    }),

    /* ATeam Invitation */
    getATeamInvited: builder.query({
      query: (invitationId) => ({
        url: `ateams/invitation/${invitationId}`,
        method: "GET",
      }),
      providesTags: (result, error, invitationId) => [
        { type: "AteamInvitation", id: "ALL" },
        { type: "Ateam", id: "ateamId" },
      ],
    }),
    createATeamInvitation: builder.mutation({
      query: ({ ateamId, data }) => ({
        url: `ateams/${ateamId}/invitation`,
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "ATeamInvitation", id: "ALL" }],
    }),
    applyATeamInvitation: builder.mutation({
      query: (data) => ({
        url: "ateams/apply_invitation",
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "ATeamAccount", id: "ALL" },
        { type: "ATeamAuthority", id: result?.ateam_id },
        { type: "ATeamInvitation", id: "ALL" },
      ],
    }),

    /* ATeam Members */
    getATeamMembers: builder.query({
      query: (ateamId) => ({
        url: `ateams/${ateamId}/members`,
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
      invalidatesTags: (result, error, arg) => [
        { type: "ATeamAccount", id: `${arg.ateamId}:${arg.userId}` },
        { type: "ATeamAccount", id: "ALL" },
        { type: "ATeamAuthority", id: arg.ateamId },
      ],
    }),

    /* ATeam Topics */
    getATeamTopics: builder.query({
      query: ({ ateamId, params }) => ({
        url: `/ateams/${ateamId}/topicstatus`,
        params: params ?? {},
      }),
    }),

    /* ATeam Watching Request */
    createATeamWatchingRequest: builder.mutation({
      query: ({ ateamId, date }) => ({
        url: `ateams/${ateamId}/watching_request`,
        method: "POST",
        body: date,
      }),
      invalidateTags: (result, error, arg) => [{ type: "ATeamWatchingRequest", id: "ALL" }],
    }),
    applyATeamWatchingRequest: builder.mutation({
      query: (data) => ({
        url: "ateams/apply_watching_request",
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "ATeamPTeam", id: "ALL" },
        { type: "ATeamWatchingRequest", id: "ALL" },
      ],
    }),
    getATeamRequested: builder.query({
      query: (tokenId) => ({
        url: `ateams/watching_request/${tokenId}`,
        method: "GET",
      }),
      providesTags: (result, error, tokenId) => [{ type: "AteamWatchingRequest", id: "ALL" }],
    }),
    removeWatchingPTeam: builder.mutation({
      query: ({ ateamId, pteamId }) => ({
        url: `ateams/${ateamId}/watching_pteams/${pteamId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "ATeamPTeam", id: `${arg.ateamId}:${arg.pteamId}` },
      ],
    }),

    /* PTeam */
    getPTeam: builder.query({
      query: (pteamId) => `pteams/${pteamId}`,
      providesTags: (result, error, pteamId) => [
        ...(result?.ateams.reduce(
          (ret, ateam) => [
            ...ret,
            { type: "ATeam", id: ateam.ateam_id },
            { type: "ATeamPTeam", id: `${ateam.ateam_id}:${pteamId}` },
          ],
          [{ type: "ATeamPTeam", id: "ALL" }],
        ) ?? []),
        { type: "PTeam", id: pteamId },
        ...(result?.services.reduce(
          (ret, service) => [...ret, { type: "Service", id: service.service_id }],
          [{ type: "Service", id: "ALL" }],
        ) ?? []),
      ],
    }),
    createPTeam: builder.mutation({
      query: (data) => ({
        url: "pteams",
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "PTeamAccount", id: "ALL" }],
    }),
    updatePTeam: builder.mutation({
      query: ({ pteamId, data }) => ({
        url: `pteams/${pteamId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "PTeam", id: arg.pteamId },
        { type: "PTeam", id: "ALL" },
      ],
    }),

    /* PTeam Auth Info */
    getPTeamAuthInfo: builder.query({
      query: () => "pteams/auth_info",
      /* No tags to provide */
    }),

    /* PTeam Auth */
    getPTeamAuth: builder.query({
      query: (pteamId) => `pteams/${pteamId}/authority`,
      transformResponse: _responseListToDictConverter("user_id", "authorities"),
      providesTags: (result, error, pteamId) => [{ type: "PTeamAuthority", id: pteamId }],
    }),
    updatePTeamAuth: builder.mutation({
      query: ({ pteamId, data }) => ({
        url: `pteams/${pteamId}/authority`,
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "PTeamAuthority", id: arg.pteamId }],
    }),

    /* PTeam Invitation */
    getPTeamInvitation: builder.query({
      query: (invitationId) => ({
        url: `pteams/invitation/${invitationId}`,
      }),
      providesTags: (result, error, invitationId) => [
        { type: "PTeam", id: result?.pteam_id },
        { type: "PTeamInvitation", id: "ALL" },
      ],
    }),
    createPTeamInvitation: builder.mutation({
      query: ({ pteamId, data }) => ({
        url: `pteams/${pteamId}/invitation`,
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "PTeamInvitation", id: "ALL" }],
    }),
    applyPTeamInvitation: builder.mutation({
      query: (data) => ({
        url: "pteams/apply_invitation",
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "PTeamAccount", id: "ALL" },
        { type: "PTeamAuthority", id: result?.pteam_id },
        { type: "PTeamInvitation", id: "ALL" },
      ],
    }),

    /* PTeam Members */
    getPTeamMembers: builder.query({
      query: (pteamId) => `pteams/${pteamId}/members`,
      providesTags: (result, error, pteamId) => [
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
    deletePTeamMember: builder.mutation({
      query: ({ pteamId, userId }) => ({
        url: `pteams/${pteamId}/members/${userId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "PTeamAccount", id: `${arg.pteamId}:${arg.userId}` },
        { type: "PTeamAccount", id: "ALL" },
        { type: "PTeamAuthority", id: arg.pteamId },
      ],
    }),

    /* PTeam Service */
    updatePTeamService: builder.mutation({
      query: ({ pteamId, serviceId, data }) => ({
        url: `pteams/${pteamId}/services/${serviceId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "Service", id: arg.serviceId },
        { type: "Ticket", id: "ALL" },
      ],
    }),
    deletePTeamService: builder.mutation({
      query: ({ pteamId, serviceName }) => ({
        url: `pteams/${pteamId}/tags`,
        params: { service: serviceName },
        method: "DELETE",
      }),
      invalidatesTags: (result, error, arg) => [{ type: "Service", id: "ALL" }],
    }),

    /* PTeam Service Tags Summary */
    getPTeamServiceTagsSummary: builder.query({
      query: ({ pteamId, serviceId }) => ({
        url: `pteams/${pteamId}/services/${serviceId}/tags/summary`,
        method: "GET",
      }),
      providesTags: (result, error, arg) => [
        { type: "Ticket", id: "ALL" },
        { type: "Threat", id: "ALL" },
        { type: "CurrentTicketStatus", id: "ALL" },
        { type: "Service", id: "ALL" },
      ],
    }),

    /* PTeam Service Tagged TopicId */
    getPTeamServiceTaggedTopicIds: builder.query({
      query: ({ pteamId, serviceId, tagId }) => ({
        url: `pteams/${pteamId}/services/${serviceId}/tags/${tagId}/topic_ids`,
        method: "GET",
      }),
      providesTags: (result, error, arg) => [
        { type: "Ticket", id: "ALL" },
        { type: "Threat", id: "ALL" },
        { type: "CurrentTicketStatus", id: "ALL" },
        { type: "Service", id: "ALL" },
      ],
    }),

    /* PTeam Service Thumbnail */
    getPTeamServiceThumbnail: builder.query({
      query: ({ pteamId, serviceId }) => ({
        url: `pteams/${pteamId}/services/${serviceId}/thumbnail`,
        responseHandler: async (response) => await blobToDataURL(await response.blob()),
      }),
    }),

    /* PTeam Ticket Related To Service TopicTag */
    getTicketsRelatedToServiceTopicTag: builder.query({
      query: ({ pteamId, serviceId, topicId, tagId }) => ({
        url: `pteams/${pteamId}/services/${serviceId}/topics/${topicId}/tags/${tagId}/tickets`,
        method: "GET",
      }),
      providesTags: (result, error, arg) => [
        ...(result
          ? result.map((ticket) => ({ type: "CurrentTicketStatus", id: ticket.ticket_id }))
          : []),
        { type: "Ticket", id: "ALL" },
        { type: "Threat", id: "ALL" },
        { type: "Service", id: "ALL" },
      ],
    }),

    /* PTeam Watchers */
    removeWatcherATeam: builder.mutation({
      query: ({ pteamId, ateamId }) => ({
        url: `pteams/${pteamId}/watchers/${ateamId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "ATeamPTeam", id: `${arg.ateamId}:${arg.pteamId}` },
      ],
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
      invalidatesTags: (result, error, arg) => [{ type: "Tag", id: "ALL" }],
    }),

    /* tag */
    getTags: builder.query({
      query: () => ({
        url: "tags",
      }),
      providesTags: (result, error) => [{ type: "Tag", id: "ALL" }],
    }),

    createTag: builder.mutation({
      query: (data) => ({
        url: "tags",
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "Tag", id: "ALL" }],
    }),

    /* Ticket Status */
    createTicketStatus: builder.mutation({
      query: ({ pteamId, serviceId, ticketId, data }) => ({
        url: `pteams/${pteamId}/services/${serviceId}/ticketstatus/${ticketId}`,
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "CurrentTicketStatus", id: "ALL" },
        { type: "CurrentTicketStatus", id: arg.ticketId },
      ],
    }),

    /* TopicAction */
    getPTeamTopicActions: builder.query({
      query: ({ topicId, pteamId }) => ({
        url: `topics/${topicId}/actions/pteam/${pteamId}`,
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
    getTopicActions: builder.query({
      query: (topicId) => ({
        url: `topics/${topicId}/actions/user/me`,
        method: "GET",
      }),
      providesTags: (result, error, arg) => [
        ...(result?.reduce(
          (ret, action) => [...ret, { type: "TopicAction", id: action.action_id }],
          [],
        ) ?? []),
        { type: "TopicAction", id: "ALL" },
      ],
    }),

    /* Topic Comment */
    getATeamTopicComment: builder.query({
      query: ({ ateamId, topicId }) => `ateams/${ateamId}/topiccomment/${topicId}`,
      providesTags: (result, error, arg) => [
        { type: "ATeamTopicComment", id: `${arg.ateamId}:${arg.topicId}` },
        { type: "ATeamTopicComment", id: `ALL:${arg.topicId}` },
      ],
    }),
    createATeamTopicComment: builder.mutation({
      query: ({ ateamId, topicId, data }) => ({
        url: `ateams/${ateamId}/topiccomment/${topicId}`,
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "ATeamTopicComment", id: `${arg.ateamId}:${arg.topicId}` },
      ],
    }),
    updateATeamTopicComment: builder.mutation({
      query: ({ ateamId, topicId, commentId, data }) => ({
        url: `ateams/${ateamId}/topiccomment/${topicId}/${commentId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "ATeamTopicComment", id: `${arg.ateamId}:${arg.topicId}` },
      ],
    }),
    deleteATeamTopicComment: builder.mutation({
      query: ({ ateamId, topicId, commentId }) => ({
        url: `ateams/${ateamId}/topiccomment/${topicId}/${commentId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "ATeamTopicComment", id: `${arg.ateamId}:${arg.topicId}` },
      ],
    }),

    /* Topics */
    getTopic: builder.query({
      query: (topicId) => `/topics/${topicId}`,
      providesTags: (result, error, topicId) => [{ type: "Topic", id: `${topicId}` }],
    }),
    searchTopics: builder.query({
      query: (params) => ({
        url: "topics/search",
        params: params,
      }),
      /* No tags to provide */
    }),
    createTopic: builder.mutation({
      query: ({ topicId, data }) => ({
        url: `topics/${topicId}`,
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "Threat", id: "ALL" }],
    }),
    updateTopic: builder.mutation({
      query: ({ topicId, data }) => ({
        url: `topics/${topicId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "Threat", id: "ALL" },
        { type: "Topic", id: `${arg.topicId}` },
      ],
    }),
    deleteTopic: builder.mutation({
      query: (topicId) => ({
        url: `topics/${topicId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, topicId) => [
        { type: "ATeamTopicComment", id: `ALL:${topicId}` },
        { type: "Threat", id: "ALL" },
        { type: "Topic", id: `${topicId}` },
      ],
    }),

    /* User */
    getUserMe: builder.query({
      query: () => "users/me",
      providesTags: (result, error, _) => [
        { type: "Account", id: result?.user_id },
        ...(result?.ateams.reduce(
          (ret, ateam) => [
            ...ret,
            { type: "ATeam", id: ateam.ateam_id },
            { type: "ATeamAccount", id: `${ateam.ateam_id}:${result?.user_id}` },
          ],
          [{ type: "ATeamAccount", id: "ALL" }],
        ) ?? []),
        ...(result?.pteams.reduce(
          (ret, pteam) => [
            ...ret,
            { type: "PTeam", id: pteam.pteam_id },
            { type: "PTeamAccount", id: `${pteam.pteam_id}:${result?.user_id}` },
          ],
          [{ type: "PTeamAccount", id: "ALL" }],
        ) ?? []),
      ],
    }),
    tryLogin: builder.mutation({
      query: () => "users/me",
      method: "GET",
    }),
    createUser: builder.mutation({
      query: (data) => ({
        url: "users",
        method: "POST",
        body: data,
      }),
    }),
    updateUser: builder.mutation({
      query: ({ userId, data }) => ({
        url: `users/${userId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [{ type: "Account", id: arg.userId }],
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
  useGetATeamAuthInfoQuery,
  useGetATeamAuthQuery,
  useUpdateATeamAuthMutation,
  useCreateATeamInvitationMutation,
  useApplyATeamInvitationMutation,
  useGetATeamInvitedQuery,
  useGetATeamMembersQuery,
  useGetATeamTopicsQuery,
  useGetATeamRequestedQuery,
  useGetPTeamTopicActionsQuery,
  useGetTopicQuery,
  useGetTopicActionsQuery,
  useDeleteATeamMemberMutation,
  useGetATeamTopicCommentQuery,
  useCreateATeamTopicCommentMutation,
  useUpdateATeamTopicCommentMutation,
  useDeleteATeamTopicCommentMutation,
  useCreateATeamWatchingRequestMutation,
  useApplyATeamWatchingRequestMutation,
  useRemoveWatchingPTeamMutation,
  useGetPTeamQuery,
  useCreatePTeamMutation,
  useUpdatePTeamMutation,
  useUpdatePTeamAuthMutation,
  useUpdateTopicMutation,
  useGetPTeamAuthInfoQuery,
  useGetPTeamAuthQuery,
  useGetPTeamInvitationQuery,
  useCreatePTeamInvitationMutation,
  useApplyPTeamInvitationMutation,
  useGetPTeamMembersQuery,
  useDeletePTeamMemberMutation,
  useDeleteTopicMutation,
  useUploadSBOMFileMutation,
  useUpdatePTeamServiceMutation,
  useDeletePTeamServiceMutation,
  useGetPTeamServiceTagsSummaryQuery,
  useGetPTeamServiceTaggedTopicIdsQuery,
  useGetPTeamServiceThumbnailQuery,
  useGetTicketsRelatedToServiceTopicTagQuery,
  useRemoveWatcherATeamMutation,
  useCreateTicketStatusMutation,
  useSearchTopicsQuery,
  useGetUserMeQuery,
  useTryLoginMutation,
  useCreateUserMutation,
  useUpdateUserMutation,
  useCreateTopicMutation,
  useGetTagsQuery,
  useCreateTagMutation,
  useCheckMailMutation,
  useCheckSlackMutation,
} = tcApi;

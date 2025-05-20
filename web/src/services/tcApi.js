import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import Firebase from "../utils/Firebase";
import Supabase from "../utils/Supabase";
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

const _getBearerToken = {
  supabase: Supabase.getBearerToken.bind(Supabase),
  firebase: Firebase.getBearerToken.bind(Firebase),
}[import.meta.env.VITE_AUTH_SERVICE];

export const tcApi = createApi({
  reducerPath: "tcApi",
  baseQuery: fetchBaseQuery({
    baseUrl: import.meta.env.VITE_API_BASE_URL,
    prepareHeaders: async (headers) => {
      const token = await _getBearerToken();
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
    /* Action */
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

    /* Dependency */
    getDependencies: builder.query({
      query: ({ pteamId, serviceId }) => ({
        url: `pteams/${pteamId}/services/${serviceId}/dependencies`,
        method: "GET",
      }),
      providesTags: (result, error, arg) => [{ type: "Service", id: "ALL" }],
    }),

    /* PTeam */
    getPTeam: builder.query({
      query: (pteamId) => `pteams/${pteamId}`,
      providesTags: (result, error, pteamId) => [
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
      invalidatesTags: (result, error, arg) => [{ type: "PTeamAccountRole", id: "ALL" }],
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
        { type: "PTeamAccountRole", id: "ALL" },
        { type: "PTeamInvitation", id: "ALL" },
      ],
    }),

    /* PTeam Member */
    getPTeamMembers: builder.query({
      query: (pteamId) => `pteams/${pteamId}/members`,
      providesTags: (result, error, pteamId) => [
        ...(result
          ? Object.keys(result).reduce(
              (ret, userId) => [...ret, { type: "Account", id: userId }],
              [],
            )
          : []),
        { type: "PTeam", id: "ALL" },
        { type: "PTeamAccountRole", id: "ALL" },
      ],
      transformResponse: _responseListToDictConverter("user_id"),
    }),
    deletePTeamMember: builder.mutation({
      query: ({ pteamId, userId }) => ({
        url: `pteams/${pteamId}/members/${userId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "PTeamAccountRole", id: `${arg.pteamId}:${arg.userId}` },
        { type: "PTeamAccountRole", id: "ALL" },
      ],
    }),
    updatePTeamMember: builder.mutation({
      query: ({ pteamId, userId, data }) => ({
        url: `pteams/${pteamId}/members/${userId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "PTeamAccountRole", id: `${arg.pteamId}:${arg.userId}` },
        { type: "PTeamAccountRole", id: "ALL" },
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
      query: ({ pteamId, serviceId }) => ({
        url: `pteams/${pteamId}/services/${serviceId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, arg) => [{ type: "Service", id: "ALL" }],
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
        { type: "TicketStatus", id: "ALL" },
        { type: "Service", id: "ALL" },
      ],
    }),

    /* PTeam Service Thumbnail */
    getPTeamServiceThumbnail: builder.query({
      query: ({ pteamId, serviceId }) => ({
        url: `pteams/${pteamId}/services/${serviceId}/thumbnail`,
        responseHandler: async (response) => await blobToDataURL(await response.blob()),
      }),
      providesTags: (result, error, arg) => [
        { type: "Service", id: "ALL" },
        { type: "Service.thumbnail", id: arg.serviceId },
      ],
    }),

    updatePTeamServiceThumbnail: builder.mutation({
      query: ({ pteamId, serviceId, imageFile }) => {
        const imageFileData = new FormData();
        imageFileData.append("uploaded", imageFile);
        return {
          url: `pteams/${pteamId}/services/${serviceId}/thumbnail`,
          method: "POST",
          body: imageFileData,
        };
      },
      invalidatesTags: (result, error, arg) => [{ type: "Service.thumbnail", id: arg.serviceId }],
    }),

    deletePTeamServiceThumbnail: builder.mutation({
      query: ({ pteamId, serviceId }) => ({
        url: `pteams/${pteamId}/services/${serviceId}/thumbnail`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, arg) => [{ type: "Service.thumbnail", id: arg.serviceId }],
    }),

    /* PTeam packages Summary */
    getPTeamPackagesSummary: builder.query({
      query: ({ pteamId, serviceId }) => ({
        url: `pteams/${pteamId}/packages/summary`,
        method: "GET",
        params: { service_id: serviceId },
      }),
      providesTags: (result, error, arg) => [
        { type: "Ticket", id: "ALL" },
        { type: "Threat", id: "ALL" },
        { type: "TicketStatus", id: "ALL" },
        { type: "Service", id: "ALL" },
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

    /* Tag */
    getTags: builder.query({
      query: () => ({
        url: "tags",
      }),
      providesTags: (result, error) => [{ type: "Tag", id: "ALL" }],
    }),

    getTag: builder.query({
      query: (tagId) => ({
        url: `tags/${tagId}`,
      }),
    }),

    /* Threat */
    getThreat: builder.query({
      query: (threatId) => ({
        url: `threats/${threatId}`,
        method: "GET",
      }),
      providesTags: (result, error, threatId) => [
        { type: "Threat", id: "ALL" },
        { type: "Threat", id: threatId },
        { type: "Service", id: "ALL" },
      ],
    }),
    updateThreat: builder.mutation({
      query: ({ threatId, data }) => ({
        url: `threats/${threatId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "Threat", id: arg.threatId },
        { type: "Ticket", id: "ALL" },
      ],
    }),

    /* Ticket */
    getTickets: builder.query({
      query: ({ pteamId, serviceId, topicId, tagId }) => ({
        url: `pteams/${pteamId}/services/${serviceId}/topics/${topicId}/tags/${tagId}/tickets`,
        method: "GET",
      }),
      providesTags: (result, error, arg) => [
        ...(result ? result.map((ticket) => ({ type: "TicketStatus", id: ticket.ticket_id })) : []),
        { type: "Ticket", id: "ALL" },
        { type: "Threat", id: "ALL" },
        { type: "Service", id: "ALL" },
      ],
    }),

    /* Ticket Status */
    updateTicketStatus: builder.mutation({
      query: ({ pteamId, serviceId, ticketId, data }) => ({
        url: `pteams/${pteamId}/services/${serviceId}/ticketstatus/${ticketId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "TicketStatus", id: "ALL" },
        { type: "TicketStatus", id: arg.ticketId },
      ],
    }),

    /* Topic */
    getTopic: builder.query({
      query: (topicId) => `/topics/${topicId}`,
      providesTags: (result, error, topicId) => [{ type: "Topic", id: `${topicId}` }],
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
        { type: "Threat", id: "ALL" },
        { type: "Topic", id: `${topicId}` },
      ],
    }),

    /* Topic Action */
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

    /* User */
    getUserMe: builder.query({
      query: () => "users/me",
      providesTags: (result, error, _) => [
        { type: "Account", id: result?.user_id },
        ...(result?.pteam_roles.reduce(
          (ret, pteam_role) => [
            ...ret,
            { type: "PTeam", id: pteam_role.pteam.pteam_id },
            { type: "PTeamAccountRole", id: `${pteam_role.pteam.pteam_id}:${result?.user_id}` },
          ],
          [{ type: "PTeamAccountRole", id: "ALL" }],
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

    /* Vuln */
    getVulnActions: builder.query({
      query: (vulnId) => ({
        url: `vulns/${vulnId}/actions`,
      }),
      providesTags: (result, error, arg) => [
        ...(result?.reduce(
          (ret, action) => [...ret, { type: "VulnAction", id: action.action_id }],
          [],
        ) ?? []),
        { type: "VulnAction", id: "ALL" },
      ],
    }),
    getVulns: builder.query({
      query: (params) => ({
        url: "vulns",
        params: params,
      }),
      providesTags: (result, error, arg) => [
        ...(result?.vulns.reduce((ret, vuln) => [...ret, { type: "Vuln", id: vuln.vuln_id }], []) ??
          []),
        { type: "Vuln", id: "ALL" },
        { type: "Service", id: "ALL" },
      ],
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
  useGetDependenciesQuery,
  useGetPTeamQuery,
  useCreatePTeamMutation,
  useUpdatePTeamMutation,
  useGetPTeamInvitationQuery,
  useCreatePTeamInvitationMutation,
  useApplyPTeamInvitationMutation,
  useGetPTeamMembersQuery,
  useDeletePTeamMemberMutation,
  useUpdatePTeamMemberMutation,
  useUpdatePTeamServiceMutation,
  useDeletePTeamServiceMutation,
  useGetPTeamServiceTaggedTopicIdsQuery,
  useGetPTeamServiceThumbnailQuery,
  useUpdatePTeamServiceThumbnailMutation,
  useDeletePTeamServiceThumbnailMutation,
  useGetPTeamPackagesSummaryQuery,
  useUploadSBOMFileMutation,
  useGetTagsQuery,
  useGetTagQuery,
  useGetThreatQuery,
  useUpdateThreatMutation,
  useGetTicketsQuery,
  useUpdateTicketStatusMutation,
  useGetTopicQuery,
  useCreateTopicMutation,
  useUpdateTopicMutation,
  useDeleteTopicMutation,
  useGetPTeamTopicActionsQuery,
  useGetTopicActionsQuery,
  useGetUserMeQuery,
  useGetVulnActionsQuery,
  useGetVulnsQuery,
  useTryLoginMutation,
  useCreateUserMutation,
  useUpdateUserMutation,
  useCheckMailMutation,
  useCheckSlackMutation,
} = tcApi;

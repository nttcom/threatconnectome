import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

const _responseListToDictConverter =
  (keyName, valueName = undefined) =>
  async (response) =>
    (await response.json()).reduce((ret, item) => {
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
    /* Action Log */
    createActionLog: builder.mutation({
      query: (data) => ({
        url: "actionlogs",
        method: "POST",
        body: data,
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
    }),
    updatePTeam: builder.mutation({
      query: ({ pteamId, data }) => ({
        url: `/pteams/${pteamId}`,
        method: "PUT",
        body: data,
      }),
    }),

    /* PTeam Auth Info */
    getPTeamAuthInfo: builder.query({
      query: () => "pteams/auth_info",
    }),

    /* PTeam Auth */
    getPTeamAuth: builder.query({
      query: (pteamId) => ({
        url: `pteams/${pteamId}/authority`,
        responseHandler: _responseListToDictConverter("user_id", "authorities"),
      }),
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
    }),

    /* PTeam Members */
    getPTeamMembers: builder.query({
      query: (pteamId) => ({
        url: `pteams/${pteamId}/members`,
        responseHandler: _responseListToDictConverter("user_id"),
      }),
    }),
    deletePTeamMember: builder.mutation({
      query: ({ pteamId, userId }) => ({
        url: `pteams/${pteamId}/members/${userId}`,
        method: "DELETE",
      }),
    }),

    /* PTeam Service */
    updatePTeamService: builder.mutation({
      query: ({ pteamId, serviceId, data }) => ({
        url: `pteams/${pteamId}/services/${serviceId}/`,
        method: "PUT",
        body: data,
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

    /* Topics */
    searchTopics: builder.query({
      query: (params) => ({
        url: "topics/search",
        params: params,
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
  useCreateActionLogMutation,
  useGetPTeamQuery,
  useCreatePTeamMutation,
  useUpdatePTeamMutation,
  useUpdatePTeamAuthMutation,
  useGetPTeamAuthInfoQuery,
  useGetPTeamAuthQuery,
  useCreatePTeamInvitationMutation,
  useApplyPTeamInvitationMutation,
  useGetPTeamMembersQuery,
  useDeletePTeamMemberMutation,
  useUploadSBOMFileMutation,
  useUpdatePTeamServiceMutation,
  useCreateTicketStatusMutation,
  useSearchTopicsQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useCheckMailMutation,
  useCheckSlackMutation,
} = tcApi;

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

const _responseListToDictConverter =
  (keyName, valueName = undefined) =>
  async (response) =>
    (await response.json()).reduce(
      (ret, val) => ({
        ...ret,
        [val[keyName]]: valueName ? val[valueName] : val,
      }),
      {},
    );

export const tcApi = createApi({
  reducerPath: "tcApi",
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.REACT_APP_API_BASE_URL,
    prepareHeaders: (headers, { getState }) => {
      const token = getState().auth?.token; // filled by slices/auth::setAuthToken
      if (token) {
        headers.set("authorization", `Bearer ${token}`);
      }
      return headers;
    },
  }),
  endpoints: (builder) => ({
    /* PTeam */
    getPTeam: builder.query({
      query: (pteamId) => `pteams/${pteamId}`,
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
      providesTags: (result, error, id) => [{ type: "PTeamAuth", id }],
    }),
    updatePTeamAuth: builder.mutation({
      query: ({ pteamId, data }) => ({
        url: `pteams/${pteamId}/authority`,
        method: "POST",
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: "PTeamAuth", id }],
    }),

    /* PTeam Members */
    getPTeamMembers: builder.query({
      query: (pteamId) => ({
        url: `pteams/${pteamId}/members`,
        responseHandler: _responseListToDictConverter("user_id"),
      }),
    }),
  }),
});

export const {
  useGetPTeamQuery,
  useUpdatePTeamAuthMutation,
  useGetPTeamAuthInfoQuery,
  useGetPTeamAuthQuery,
  useGetPTeamMembersQuery,
} = tcApi;

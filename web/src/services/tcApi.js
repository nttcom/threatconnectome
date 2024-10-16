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
      /* Note: access token is stored in auth.token via firebaseApi or cookie */
      const token = getState().auth.token;
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

    /* PTeam Members */
    getPTeamMembers: builder.query({
      query: (pteamId) => ({
        url: `pteams/${pteamId}/members`,
        responseHandler: _responseListToDictConverter("user_id"),
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
  }),
});

export const {
  useGetPTeamQuery,
  useUpdatePTeamAuthMutation,
  useGetPTeamAuthInfoQuery,
  useGetPTeamAuthQuery,
  useGetPTeamMembersQuery,
  useUploadSBOMFileMutation,
} = tcApi;

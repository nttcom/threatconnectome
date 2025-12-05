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
      query: ({ pteamId, serviceId, packageId, offset, limit }) => ({
        url: `pteams/${pteamId}/dependencies`,
        method: "GET",
        params: {
          service_id: serviceId,
          package_id: packageId,
          offset: offset,
          limit: limit,
        },
      }),
      providesTags: (result, error, arg) => [{ type: "Service", id: "ALL" }],
    }),
    getDependency: builder.query({
      query: ({ pteamId, dependencyId }) => ({
        url: `pteams/${pteamId}/dependencies/${dependencyId}`,
        method: "GET",
      }),
      providesTags: (result, error, arg) => [
        { type: "Service", id: "ALL" },
        { type: "Dependency", id: arg.dependencyId },
      ],
    }),

    /* Insight  */
    getInsight: builder.query({
      query: (ticketId) => `tickets/${ticketId}/insight`,
      providesTags: (result, error, ticketId) => [
        { type: "Service", id: "ALL" },
        { type: "Threat", id: "ALL" },
      ],
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
    getPTeamServices: builder.query({
      query: (pteamId) => `pteams/${pteamId}/services`,
      providesTags: (result, error, pteamId) => [
        ...(result?.map((service) => ({ type: "Service", id: service.service_id })) ?? []),
        { type: "Service", id: "ALL" },
      ],
    }),
    updatePTeamService: builder.mutation({
      query: ({ pteamId, serviceId, data }) => ({
        url: `pteams/${pteamId}/services/${serviceId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) =>
        result
          ? [
              { type: "Service", id: arg.serviceId },
              { type: "Ticket", id: "ALL" },
            ]
          : [],
    }),
    deletePTeamService: builder.mutation({
      query: ({ pteamId, serviceId }) => ({
        url: `pteams/${pteamId}/services/${serviceId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, arg) => [
        ...(result?.map((service) => ({ type: "Service", id: service.service_id })) ?? []),
        { type: "Service", id: "ALL" },
      ],
    }),

    /* PTeam  */
    getPTeamVulnIdsTiedToServicePackage: builder.query({
      query: ({ pteamId, serviceId, packageId, relatedTicketStatus }) => ({
        url: `pteams/${pteamId}/vuln_ids`,
        method: "GET",
        params: {
          service_id: serviceId,
          package_id: packageId,
          related_ticket_status: relatedTicketStatus,
        },
      }),
      providesTags: (result, error, arg) => [
        { type: "Ticket", id: "ALL" },
        { type: "TicketStatus", id: "ALL" },
        { type: "Threat", id: "ALL" },
        { type: "Service", id: "ALL" },
      ],
    }),

    getPTeamTicketCountsTiedToServicePackage: builder.query({
      query: ({ pteamId, serviceId, packageId, relatedTicketStatus }) => ({
        url: `pteams/${pteamId}/ticket_counts`,
        method: "GET",
        params: {
          service_id: serviceId,
          package_id: packageId,
          related_ticket_status: relatedTicketStatus,
        },
      }),
      providesTags: (result, error, arg) => [
        { type: "Ticket", id: "ALL" },
        { type: "TicketStatus", id: "ALL" },
        { type: "Threat", id: "ALL" },
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
      invalidatesTags: (result, error, arg) => [{ type: "Service", id: "ALL" }],
    }),

    /* Ticket */
    getTickets: builder.query({
      query: ({ assignedToMe, pteamIds, offset, limit, sortKeys, excludeStatuses, cveIds }) => ({
        url: "tickets",
        method: "GET",
        params: {
          assigned_to_me: assignedToMe,
          pteam_ids: pteamIds,
          offset: offset,
          limit: limit,
          sort_keys: sortKeys,
          exclude_statuses: excludeStatuses,
          cve_ids: cveIds,
        },
      }),
      providesTags: (result, error, arg) => [
        ...(result?.tickets?.map((ticket) => ({ type: "Ticket", id: ticket.ticket_id })) ?? []),
        { type: "Service", id: "ALL" },
        { type: "Ticket", id: "ALL" },
        { type: "TicketStatus", id: "ALL" },
        { type: "Threat", id: "ALL" },
      ],
    }),
    getPteamTickets: builder.query({
      query: ({ pteamId, serviceId, vulnId, packageId }) => ({
        url: `pteams/${pteamId}/tickets`,
        method: "GET",
        params: {
          service_id: serviceId,
          vuln_id: vulnId,
          package_id: packageId,
        },
      }),
      providesTags: (result, error, arg) => [
        ...(result ? result.map((ticket) => ({ type: "TicketStatus", id: ticket.ticket_id })) : []),
        { type: "Ticket", id: "ALL" },
        { type: "Threat", id: "ALL" },
        { type: "Service", id: "ALL" },
      ],
    }),

    updateTicket: builder.mutation({
      query: ({ pteamId, ticketId, data }) => ({
        url: `pteams/${pteamId}/tickets/${ticketId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, arg) => [
        { type: "Ticket", id: "ALL" },
        { type: "Ticket", id: arg.ticketId },
        { type: "TicketStatus", id: "ALL" },
        { type: "TicketStatus", id: arg.ticketId },
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
    deleteUser: builder.mutation({
      query: () => ({
        url: "users/me",
        method: "DELETE",
      }),
    }),

    /* Vuln */
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
    getVuln: builder.query({
      query: (vulnId) => `/vulns/${vulnId}`,
      providesTags: (result, error, vulnId) => [{ type: "Vuln", id: `${vulnId}` }],
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
  useGetDependenciesQuery,
  useGetDependencyQuery,
  useGetInsightQuery,
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
  useGetPTeamVulnIdsTiedToServicePackageQuery,
  useGetPTeamTicketCountsTiedToServicePackageQuery,
  useGetPTeamServicesQuery,
  useGetPTeamServiceThumbnailQuery,
  useUpdatePTeamServiceThumbnailMutation,
  useDeletePTeamServiceThumbnailMutation,
  useGetPTeamPackagesSummaryQuery,
  useUploadSBOMFileMutation,
  useGetTicketsQuery,
  useGetPteamTicketsQuery,
  useUpdateTicketMutation,
  useGetUserMeQuery,
  useGetVulnsQuery,
  useGetVulnQuery,
  useTryLoginMutation,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
  useCheckMailMutation,
  useCheckSlackMutation,
} = tcApi;

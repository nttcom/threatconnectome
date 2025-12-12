import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

// @ts-expect-error TS7016
import Firebase from "../utils/Firebase.js";
// @ts-expect-error TS7016
import Supabase from "../utils/Supabase.js";
// @ts-expect-error TS7016
import { blobToDataURL } from "../utils/func.js";

import type {
  CreateLogActionlogsPostData,
  ActionLogResponse,
  DependencyResponse,
  PTeamInfo,
  CreatePteamPteamsPostData,
  PTeamInvitationResponse,
  ApplyInvitationPteamsApplyInvitationPostData,
  PTeamMemberUpdateResponse,
  UpdatePteamServicePteamsPteamIdServicesServiceIdPutData,
  PTeamServiceUpdateResponse,
  GetMyUserInfoUsersMeGetData,
  TicketResponse,
  UpdateUserUsersUserIdPutData,
  UserResponse,
  GetDependenciesPteamsPteamIdDependenciesGetData,
  GetDependencyPteamsPteamIdDependenciesDependencyIdGetData,
  InsightResponse,
  GetInsightTicketsTicketIdInsightGetData,
  GetPteamPteamsPteamIdGetData,
  UpdatePteamPteamsPteamIdPutData,
  PTeamInviterResponse,
  InvitedPteamPteamsInvitationInvitationIdGetData,
  CreateInvitationPteamsPteamIdInvitationPostData,
  DeleteMemberPteamsPteamIdMembersUserIdDeleteData,
  UpdatePteamMemberPteamsPteamIdMembersUserIdPutData,
  PTeamServiceResponse,
  GetPteamServicesPteamsPteamIdServicesGetData,
  RemoveServicePteamsPteamIdServicesServiceIdDeleteData,
  GetVulnIdsTiedToServicePackagePteamsPteamIdVulnIdsGetData,
  ServicePackageTicketCountsSolvedUnsolved,
  ServicePackageVulnsSolvedUnsolved,
  GetTicketCountsTiedToServicePackagePteamsPteamIdTicketCountsGetData,
  GetServiceThumbnailPteamsPteamIdServicesServiceIdThumbnailGetData,
  UploadServiceThumbnailPteamsPteamIdServicesServiceIdThumbnailPostData,
  RemoveServiceThumbnailPteamsPteamIdServicesServiceIdThumbnailDeleteData,
  PTeamPackagesSummary,
  GetPteamPackagesSummaryPteamsPteamIdPackagesSummaryGetData,
  UploadPteamSbomFilePteamsPteamIdUploadSbomFilePostData,
  GetTicketsTicketsGetData,
  TicketListResponse,
  GetTicketsByServiceIdAndPackageIdAndVulnIdPteamsPteamIdTicketsGetData,
  UpdateTicketPteamsPteamIdTicketsTicketIdPutData,
  CreateUserUsersPostData,
  DeleteUserUsersMeDeleteData,
  VulnsListResponse,
  GetVulnsVulnsGetData,
  CheckEmailExternalEmailCheckPostData,
  CheckWebhookUrlExternalSlackCheckPostData,
  GetPteamMembersPteamsPteamIdMembersGetData,
  PteamMemberGetResponse,
  GetVulnVulnsVulnIdGetResponses,
  GetVulnVulnsVulnIdGetData,
} from "../../types/types.gen.ts";

const TAG_TYPES_LIST = [
  "Service",
  "Dependency",
  "Threat",
  "Ticket",
  "TicketStatus",
  "PTeam",
  "PTeamInvitation",
  "PTeamAccountRole",
  "Account",
  "Vuln",
  "Service.thumbnail",
] as const;

type AllowedTagTypes = (typeof TAG_TYPES_LIST)[number];

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
  tagTypes: TAG_TYPES_LIST,
  endpoints: (builder) => ({
    /* Action Log */
    createActionLog: builder.mutation<ActionLogResponse, CreateLogActionlogsPostData>({
      query: (arg) => ({
        url: "actionlogs",
        method: "POST",
        body: arg.body,
      }),
    }),

    /* Dependency */
    getDependencies: builder.query<
      Array<DependencyResponse>,
      GetDependenciesPteamsPteamIdDependenciesGetData
    >({
      query: (arg) => ({
        url: `pteams/${arg.path.pteam_id}/dependencies`,
        method: "GET",
        params: {
          service_id: arg?.query?.service_id,
          package_id: arg?.query?.package_id,
          offset: arg?.query?.offset,
          limit: arg?.query?.limit,
        },
      }),
      providesTags: (_result, _error, _arg) => [{ type: "Service", id: "ALL" }],
    }),
    getDependency: builder.query<
      DependencyResponse,
      GetDependencyPteamsPteamIdDependenciesDependencyIdGetData
    >({
      query: (arg) => ({
        url: `pteams/${arg.path.pteam_id}/dependencies/${arg.path.dependency_id}`,
        method: "GET",
      }),
      providesTags: (_result, _error, _arg) => [
        { type: "Service", id: "ALL" },
        { type: "Dependency", id: _arg.path.dependency_id },
      ],
    }),

    /* Insight  */
    getInsight: builder.query<InsightResponse, GetInsightTicketsTicketIdInsightGetData>({
      query: (arg) => `tickets/${arg.path.ticket_id}/insight`,
      providesTags: (_result, _error, _arg) => [
        { type: "Service", id: "ALL" },
        { type: "Threat", id: "ALL" },
      ],
    }),

    /* PTeam */
    getPTeam: builder.query<PTeamInfo, GetPteamPteamsPteamIdGetData>({
      query: (arg) => `pteams/${arg.path.pteam_id}`,
      providesTags: (_result, _error, _arg) => [
        { type: "PTeam", id: _arg.path.pteam_id },
        ...(_result?.services.reduce<Array<{ type: AllowedTagTypes; id: string }>>(
          (ret, service) => [...ret, { type: "Service", id: service.service_id }],
          [{ type: "Service", id: "ALL" }],
        ) ?? []),
      ],
    }),
    createPTeam: builder.mutation<PTeamInfo, CreatePteamPteamsPostData>({
      query: (arg) => ({
        url: "pteams",
        method: "POST",
        body: arg.body,
      }),
      invalidatesTags: (_result, _error, _arg) => [{ type: "PTeamAccountRole", id: "ALL" }],
    }),
    updatePTeam: builder.mutation<PTeamInfo, UpdatePteamPteamsPteamIdPutData>({
      query: (arg) => ({
        url: `pteams/${arg.path.pteam_id}`,
        method: "PUT",
        body: arg.body,
      }),
      invalidatesTags: (_result, _error, _arg) => [
        { type: "PTeam", id: _arg.path.pteam_id },
        { type: "PTeam", id: "ALL" },
      ],
    }),

    /* PTeam Invitation */
    getPTeamInvitation: builder.query<
      PTeamInviterResponse,
      InvitedPteamPteamsInvitationInvitationIdGetData
    >({
      query: (arg) => ({
        url: `pteams/invitation/${arg.path.invitation_id}`,
      }),
      providesTags: (_result, _error, _arg) => [
        { type: "PTeam", id: _result?.pteam_id },
        { type: "PTeamInvitation", id: "ALL" },
      ],
    }),
    createPTeamInvitation: builder.mutation<
      PTeamInvitationResponse,
      CreateInvitationPteamsPteamIdInvitationPostData
    >({
      query: (arg) => ({
        url: `pteams/${arg.path.pteam_id}/invitation`,
        method: "POST",
        body: arg.body,
      }),
      invalidatesTags: (_result, _error, _arg) => [{ type: "PTeamInvitation", id: "ALL" }],
    }),
    applyPTeamInvitation: builder.mutation<PTeamInfo, ApplyInvitationPteamsApplyInvitationPostData>(
      {
        query: (arg) => ({
          url: "pteams/apply_invitation",
          method: "POST",
          body: arg.body,
        }),
        invalidatesTags: (_result, _error, _arg) => [
          { type: "PTeamAccountRole", id: "ALL" },
          { type: "PTeamInvitation", id: "ALL" },
        ],
      },
    ),

    /* PTeam Member */
    getPTeamMembers: builder.query<
      Array<PteamMemberGetResponse>,
      GetPteamMembersPteamsPteamIdMembersGetData
    >({
      query: (arg) => `pteams/${arg.path.pteam_id}/members`,

      providesTags: (_result, _error, _arg) => [
        { type: "PTeam", id: "ALL" },
        { type: "PTeamAccountRole", id: "ALL" },
        ...(_result
          ? Object.keys(_result).reduce<Array<{ type: AllowedTagTypes; id: string }>>(
              (ret, userId) => [...ret, { type: "Account", id: userId }],
              [],
            )
          : []),
      ],
    }),
    deletePTeamMember: builder.mutation<void, DeleteMemberPteamsPteamIdMembersUserIdDeleteData>({
      query: (arg) => ({
        url: `pteams/${arg.path.pteam_id}/members/${arg.path.user_id}`,
        method: "DELETE",
      }),
      invalidatesTags: (_result, _error, _arg) => [
        { type: "PTeamAccountRole", id: `${_arg.path.pteam_id}:${_arg.path.user_id}` },
        { type: "PTeamAccountRole", id: "ALL" },
      ],
    }),
    updatePTeamMember: builder.mutation<
      PTeamMemberUpdateResponse,
      UpdatePteamMemberPteamsPteamIdMembersUserIdPutData
    >({
      query: (arg) => ({
        url: `pteams/${arg.path.pteam_id}/members/${arg.path.user_id}`,
        method: "PUT",
        body: arg.body,
      }),
      invalidatesTags: (_result, _error, _arg) => [
        { type: "PTeamAccountRole", id: `${_arg.path.pteam_id}:${_arg.path.user_id}` },
        { type: "PTeamAccountRole", id: "ALL" },
      ],
    }),

    /* PTeam Service */
    getPTeamServices: builder.query<
      Array<PTeamServiceResponse>,
      GetPteamServicesPteamsPteamIdServicesGetData
    >({
      query: (arg) => `pteams/${arg.path.pteam_id}/services`,
      providesTags: (_result, _error, _arg) => [
        ...(_result?.map((service) => ({
          type: "Service" as AllowedTagTypes,
          id: service.service_id,
        })) ?? []),
        { type: "Service", id: "ALL" },
      ],
    }),
    updatePTeamService: builder.mutation<
      PTeamServiceUpdateResponse,
      UpdatePteamServicePteamsPteamIdServicesServiceIdPutData
    >({
      query: (arg) => ({
        url: `pteams/${arg.path.pteam_id}/services/${arg.path.service_id}`,
        method: "PUT",
        body: arg.body,
      }),
      invalidatesTags: (_result, _error, _arg) =>
        _result
          ? [
              { type: "Service", id: _arg.path.service_id },
              { type: "Ticket", id: "ALL" },
            ]
          : [],
    }),
    deletePTeamService: builder.mutation<
      void,
      RemoveServicePteamsPteamIdServicesServiceIdDeleteData
    >({
      query: (arg) => ({
        url: `pteams/${arg.path.pteam_id}/services/${arg.path.service_id}`,
        method: "DELETE",
      }),
      invalidatesTags: (_result, _error, _arg) => [
        { type: "Service", id: _arg.path.service_id },
        { type: "Service", id: "ALL" },
      ],
    }),

    /* PTeam  */
    getPTeamVulnIdsTiedToServicePackage: builder.query<
      ServicePackageVulnsSolvedUnsolved,
      GetVulnIdsTiedToServicePackagePteamsPteamIdVulnIdsGetData
    >({
      query: (arg) => ({
        url: `pteams/${arg.path.pteam_id}/vuln_ids`,
        method: "GET",
        params: {
          service_id: arg?.query?.service_id,
          package_id: arg?.query?.package_id,
          related_ticket_status: arg?.query?.related_ticket_status,
        },
      }),
      providesTags: (_result, _error, _arg) => [
        { type: "Ticket", id: "ALL" },
        { type: "TicketStatus", id: "ALL" },
        { type: "Threat", id: "ALL" },
        { type: "Service", id: "ALL" },
      ],
    }),

    getPTeamTicketCountsTiedToServicePackage: builder.query<
      ServicePackageTicketCountsSolvedUnsolved,
      GetTicketCountsTiedToServicePackagePteamsPteamIdTicketCountsGetData
    >({
      query: (arg) => ({
        url: `pteams/${arg.path.pteam_id}/ticket_counts`,
        method: "GET",
        params: {
          service_id: arg?.query?.service_id,
          package_id: arg?.query?.package_id,
          related_ticket_status: arg?.query?.related_ticket_status,
        },
      }),
      providesTags: (_result, _error, _arg) => [
        { type: "Ticket", id: "ALL" },
        { type: "TicketStatus", id: "ALL" },
        { type: "Threat", id: "ALL" },
        { type: "Service", id: "ALL" },
      ],
    }),

    /* PTeam Service Thumbnail */
    getPTeamServiceThumbnail: builder.query<
      void,
      GetServiceThumbnailPteamsPteamIdServicesServiceIdThumbnailGetData
    >({
      query: (arg) => ({
        url: `pteams/${arg.path.pteam_id}/services/${arg.path.service_id}/thumbnail`,
        responseHandler: async (response) => await blobToDataURL(await response.blob()),
      }),
      providesTags: (_result, _error, _arg) => [
        { type: "Service", id: "ALL" },
        { type: "Service.thumbnail", id: _arg.path.service_id },
      ],
    }),

    updatePTeamServiceThumbnail: builder.mutation<
      void,
      UploadServiceThumbnailPteamsPteamIdServicesServiceIdThumbnailPostData
    >({
      query: (arg) => {
        const imageFileData = new FormData();
        imageFileData.append("uploaded", arg.body.uploaded);
        return {
          url: `pteams/${arg.path.pteam_id}/services/${arg.path.service_id}/thumbnail`,
          method: "POST",
          body: imageFileData,
        };
      },
      invalidatesTags: (_result, _error, _arg) => [
        { type: "Service.thumbnail", id: _arg.path.service_id },
      ],
    }),

    deletePTeamServiceThumbnail: builder.mutation<
      void,
      RemoveServiceThumbnailPteamsPteamIdServicesServiceIdThumbnailDeleteData
    >({
      query: (arg) => ({
        url: `pteams/${arg.path.pteam_id}/services/${arg.path.service_id}/thumbnail`,
        method: "DELETE",
      }),
      invalidatesTags: (_result, _error, _arg) => [
        { type: "Service.thumbnail", id: _arg.path.service_id },
      ],
    }),

    /* PTeam packages Summary */
    getPTeamPackagesSummary: builder.query<
      PTeamPackagesSummary,
      GetPteamPackagesSummaryPteamsPteamIdPackagesSummaryGetData
    >({
      query: (arg) => ({
        url: `pteams/${arg.path.pteam_id}/packages/summary`,
        method: "GET",
        params: { service_id: arg.query?.service_id },
      }),
      providesTags: (_result, _error, _arg) => [
        { type: "Ticket", id: "ALL" },
        { type: "Threat", id: "ALL" },
        { type: "TicketStatus", id: "ALL" },
        { type: "Service", id: "ALL" },
      ],
    }),

    /* SBOM */
    uploadSBOMFile: builder.mutation<void, UploadPteamSbomFilePteamsPteamIdUploadSbomFilePostData>({
      query: (arg) => {
        const sbomFormData = new FormData();
        sbomFormData.append("file", arg.body.file);
        return {
          url: `pteams/${arg.path.pteam_id}/upload_sbom_file`,
          params: { service: arg.query?.service },
          method: "POST",
          body: sbomFormData,
          /* Note: Content-Type is fixed to multipart/form-data automatically. */
        };
      },
      invalidatesTags: (_result, _error, _arg) => [{ type: "Service", id: "ALL" }],
    }),

    /* Ticket */
    getTickets: builder.query<TicketListResponse, GetTicketsTicketsGetData>({
      query: (arg) => ({
        url: "tickets",
        method: "GET",
        params: {
          assigned_to_me: arg.query?.assigned_to_me,
          pteam_ids: arg.query?.pteam_ids,
          offset: arg.query?.offset,
          limit: arg.query?.limit,
          sort_keys: arg.query?.sort_keys,
          exclude_statuses: arg.query?.exclude_statuses,
          cve_ids: arg.query?.cve_ids,
        },
      }),
      providesTags: (_result, _error, _arg) => [
        ...(_result?.tickets?.map((ticket) => ({
          type: "Ticket" as AllowedTagTypes,
          id: ticket.ticket_id,
        })) ?? []),
        { type: "Service", id: "ALL" },
        { type: "Ticket", id: "ALL" },
        { type: "TicketStatus", id: "ALL" },
        { type: "Threat", id: "ALL" },
      ],
    }),
    getPteamTickets: builder.query<
      Array<TicketResponse>,
      GetTicketsByServiceIdAndPackageIdAndVulnIdPteamsPteamIdTicketsGetData
    >({
      query: (arg) => ({
        url: `pteams/${arg.path.pteam_id}/tickets`,
        method: "GET",
        params: {
          service_id: arg.query?.service_id,
          vuln_id: arg.query?.vuln_id,
          package_id: arg.query?.package_id,
        },
      }),
      providesTags: (_result, _error, _) => [
        ...(_result
          ? _result.map((ticket) => ({
              type: "TicketStatus" as AllowedTagTypes,
              id: ticket.ticket_id,
            }))
          : []),
        { type: "Ticket", id: "ALL" },
        { type: "Threat", id: "ALL" },
        { type: "Service", id: "ALL" },
      ],
    }),

    updateTicket: builder.mutation<TicketResponse, UpdateTicketPteamsPteamIdTicketsTicketIdPutData>(
      {
        query: (arg) => ({
          url: `pteams/${arg.path.pteam_id}/tickets/${arg.path.ticket_id}`,
          method: "PUT",
          body: arg.body,
        }),
        invalidatesTags: (_result, _error, _arg) => [
          { type: "Ticket", id: "ALL" },
          { type: "Ticket", id: _arg.path.ticket_id },
          { type: "TicketStatus", id: "ALL" },
          { type: "TicketStatus", id: _arg.path.ticket_id },
        ],
      },
    ),

    /* User */
    getUserMe: builder.query<UserResponse, GetMyUserInfoUsersMeGetData>({
      query: () => "users/me",
      providesTags: (_result, _error, _arg) => [
        { type: "Account", id: _result?.user_id },
        ...(_result?.pteam_roles.reduce<Array<{ type: AllowedTagTypes; id: string }>>(
          (ret, pteam_role) => [
            ...ret,
            { type: "PTeam", id: pteam_role.pteam.pteam_id },
            { type: "PTeamAccountRole", id: `${pteam_role.pteam.pteam_id}:${_result?.user_id}` },
          ],
          [{ type: "PTeamAccountRole", id: "ALL" }],
        ) ?? []),
      ],
    }),
    tryLogin: builder.mutation<UserResponse, GetMyUserInfoUsersMeGetData>({
      query: () => ({
        url: "users/me",
        method: "GET",
      }),
    }),
    createUser: builder.mutation<UserResponse, CreateUserUsersPostData>({
      query: (arg) => ({
        url: "users",
        method: "POST",
        body: arg.body,
      }),
    }),
    updateUser: builder.mutation<UserResponse, UpdateUserUsersUserIdPutData>({
      query: (arg) => ({
        url: `users/${arg.path.user_id}`,
        method: "PUT",
        body: arg.body,
      }),
      invalidatesTags: (_result, _error, _arg) => [{ type: "Account", id: _arg.path.user_id }],
    }),
    deleteUser: builder.mutation<void, DeleteUserUsersMeDeleteData>({
      query: () => ({
        url: "users/me",
        method: "DELETE",
      }),
    }),

    /* Vuln */
    getVulns: builder.query<VulnsListResponse, GetVulnsVulnsGetData>({
      query: (arg) => ({
        url: "vulns",
        params: arg.query,
      }),
      providesTags: (_result, _error, _arg) => [
        { type: "Vuln", id: "ALL" },
        { type: "Service", id: "ALL" },
        ...(_result?.vulns.reduce<Array<{ type: AllowedTagTypes; id: string }>>(
          (ret, vuln) => [...ret, { type: "Vuln", id: vuln.vuln_id }],
          [],
        ) ?? []),
      ],
    }),
    getVuln: builder.query<GetVulnVulnsVulnIdGetResponses, GetVulnVulnsVulnIdGetData>({
      query: (arg) => `/vulns/${arg.path.vuln_id}`,
      providesTags: (_result, _error, _arg) => [{ type: "Vuln", id: `${_arg.path.vuln_id}` }],
    }),

    /* External */
    checkMail: builder.mutation<void, CheckEmailExternalEmailCheckPostData>({
      query: (arg) => ({
        url: "external/email/check",
        method: "POST",
        body: arg.body,
      }),
    }),
    checkSlack: builder.mutation<void, CheckWebhookUrlExternalSlackCheckPostData>({
      query: (arg) => ({
        url: "external/slack/check",
        method: "POST",
        body: arg.body,
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

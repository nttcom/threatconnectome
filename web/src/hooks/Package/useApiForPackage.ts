import type { RelatedTicketStatus } from "../../../types/types.gen";
import { useSkipUntilAuthUserIsReady } from "../auth";
import {
  useGetDependenciesQuery,
  useGetPTeamQuery,
  useGetPTeamVulnIdsTiedToServicePackageQuery,
  useGetPTeamTicketCountsTiedToServicePackageQuery,
} from "../../services/tcApi";

export type PackageVulnCountsArgs = {
  pteamId: string;
  serviceId: string;
  packageId: string;
  getVulnIdsReady: boolean;
};

type PackageServiceQueryOptions = Omit<
  NonNullable<Parameters<typeof useGetPTeamQuery>[1]>,
  "selectFromResult"
>;

type PackageDependenciesQueryOptions = NonNullable<Parameters<typeof useGetDependenciesQuery>[1]>;

type PackagePTeamQueryOptions = NonNullable<Parameters<typeof useGetPTeamQuery>[1]>;

type PackageTicketCountsQueryOptions = NonNullable<
  Parameters<typeof useGetPTeamTicketCountsTiedToServicePackageQuery>[1]
>;

type PackageVulnIdsQueryOptions = NonNullable<
  Parameters<typeof useGetPTeamVulnIdsTiedToServicePackageQuery>[1]
>;

export type VulnIdsArgs = {
  pteamId: string;
  serviceId: string;
  packageId: string;
  relatedTicketStatus: RelatedTicketStatus;
};

export type DependenciesArgs = {
  pteamId: string;
  serviceId: string;
  packageId: string;
  offset?: number;
  limit?: number;
};

/**
 * Custom hook to retrieve the total number of solved/unsolved vulnerabilities
 */
export function usePackageVulnCounts({
  pteamId,
  serviceId,
  packageId,
  getVulnIdsReady,
}: PackageVulnCountsArgs) {
  const {
    solvedVulnCount = 0,
    error: solvedError,
    isLoading: solvedLoading,
  } = usePackageVulnIds(
    { pteamId, serviceId, packageId, relatedTicketStatus: "solved" },
    {
      skip: !getVulnIdsReady,
      selectFromResult: ({ data, error, isLoading }) => ({
        solvedVulnCount: data?.vuln_ids?.length ?? 0,
        error,
        isLoading,
      }),
    },
  );
  const {
    unsolvedVulnCount = 0,
    error: unsolvedError,
    isLoading: unsolvedLoading,
  } = usePackageVulnIds(
    { pteamId, serviceId, packageId, relatedTicketStatus: "unsolved" },
    {
      skip: !getVulnIdsReady,
      selectFromResult: ({ data, error, isLoading }) => ({
        unsolvedVulnCount: data?.vuln_ids?.length ?? 0,
        error,
        isLoading,
      }),
    },
  );

  return {
    solvedVulnCount,
    unsolvedVulnCount,
    solvedError,
    unsolvedError,
    solvedLoading,
    unsolvedLoading,
  };
}

/**
 * Custom hook to retrieve service information only
 * Pass to the RTK Query hook using the new argument format ({ path: {}, query: {} })
 */
export function usePackageService(
  pteamId: string,
  serviceId: string,
  options: PackageServiceQueryOptions = {},
) {
  const skipByAuth = useSkipUntilAuthUserIsReady();
  return useGetPTeamQuery(
    { path: { pteam_id: pteamId } },
    {
      ...options,
      skip: skipByAuth || !pteamId || options.skip,
      selectFromResult: ({ data, error, isLoading }) => ({
        service: data?.services?.find((service) => service.service_id === serviceId),
        error,
        isLoading,
      }),
    },
  );
}

/**
 * Custom Hook for Dependency Data Acquisition
 * Pass to the RTK Query hook using the new argument format ({ path: {}, query: {} })
 */
export function usePackageDependencies(
  { pteamId, serviceId, packageId, offset = 0, limit = 1000 }: DependenciesArgs,
  options: PackageDependenciesQueryOptions = {},
) {
  const skipByAuth = useSkipUntilAuthUserIsReady();
  return useGetDependenciesQuery(
    {
      path: { pteam_id: pteamId },
      query: { service_id: serviceId, package_id: packageId, offset, limit },
    },
    {
      ...options,
      skip: skipByAuth || !pteamId || !serviceId || !packageId || options.skip,
    },
  );
}

/**
 * PTeam Information Retrieval Custom Hook
 * Pass to the RTK Query hook using the new argument format ({ path: {} })
 */
export function usePackagePTeam(pteamId: string, options: PackagePTeamQueryOptions = {}) {
  const skipByAuth = useSkipUntilAuthUserIsReady();
  return useGetPTeamQuery(
    { path: { pteam_id: pteamId } },
    {
      ...options,
      skip: skipByAuth || !pteamId || options.skip,
    },
  );
}

/**
 * Custom Hook for Retrieving Vulnerability ID Lists
 * Pass to the RTK Query hook using the new argument format ({ path: {}, query: {} })
 */
export function usePackageVulnIds(
  { pteamId, serviceId, packageId, relatedTicketStatus }: VulnIdsArgs,
  options: PackageVulnIdsQueryOptions = {},
) {
  const skipByAuth = useSkipUntilAuthUserIsReady();
  return useGetPTeamVulnIdsTiedToServicePackageQuery(
    {
      path: { pteam_id: pteamId },
      query: {
        service_id: serviceId,
        package_id: packageId,
        related_ticket_status: relatedTicketStatus,
      },
    },
    {
      ...options,
      skip: skipByAuth || !pteamId || !serviceId || !packageId || options.skip,
    },
  );
}

/**
 * Custom hook for retrieving ticket counts
 * Pass to the RTK Query hook using the new argument format ({ path: {}, query: {} })
 */
export function usePackageTicketCounts(
  { pteamId, serviceId, packageId, relatedTicketStatus }: VulnIdsArgs,
  options: PackageTicketCountsQueryOptions = {},
) {
  const skipByAuth = useSkipUntilAuthUserIsReady();
  return useGetPTeamTicketCountsTiedToServicePackageQuery(
    {
      path: { pteam_id: pteamId },
      query: {
        service_id: serviceId,
        package_id: packageId,
        related_ticket_status: relatedTicketStatus,
      },
    },
    {
      ...options,
      skip: skipByAuth || !pteamId || !serviceId || !packageId || options.skip,
    },
  );
}

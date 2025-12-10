import { useSkipUntilAuthUserIsReady } from "../../hooks/auth.js";
import {
  useGetDependenciesQuery,
  useGetPTeamQuery,
  useGetPTeamVulnIdsTiedToServicePackageQuery,
  useGetPTeamTicketCountsTiedToServicePackageQuery,
} from "../../services/tcApi.js";

/**
 * solved/unsolvedの脆弱性件数をまとめて取得するカスタムフック
 */
export function usePackageVulnCounts({ pteamId, serviceId, packageId }) {
  const vulnIdsReady = !!(pteamId && serviceId && packageId);

  const {
    solvedVulnCount = 0,
    error: solvedError,
    isLoading: solvedLoading,
  } = usePackageVulnIds(
    { pteamId, serviceId, packageId, relatedTicketStatus: "solved" },
    {
      skip: !vulnIdsReady,
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
      skip: !vulnIdsReady,
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
 * service情報のみ取得するカスタムフック
 */
export function usePackageService(pteamId, serviceId, options = {}) {
  const skipByAuth = useSkipUntilAuthUserIsReady();
  return useGetPTeamQuery(pteamId, {
    ...options,
    skip: skipByAuth || !pteamId || options.skip,
    selectFromResult: ({ data, error, isLoading }) => ({
      service: data?.services?.find((service) => service.service_id === serviceId),
      error,
      isLoading,
    }),
  });
}

/**
 * 依存関係データ取得用カスタムフック
 */
export function usePackageDependencies(
  { pteamId, serviceId, packageId, offset = 0, limit = 1000 },
  options = {},
) {
  const skipByAuth = useSkipUntilAuthUserIsReady();
  return useGetDependenciesQuery(
    { pteamId, serviceId, packageId, offset, limit },
    {
      ...options,
      skip: skipByAuth || !pteamId || !serviceId || options.skip,
    },
  );
}

/**
 * PTeam情報取得用カスタムフック
 */
export function usePackagePTeam(pteamId, options = {}) {
  const skipByAuth = useSkipUntilAuthUserIsReady();
  return useGetPTeamQuery(pteamId, {
    ...options,
    skip: skipByAuth || !pteamId || options.skip,
  });
}

/**
 * 脆弱性IDリスト取得用カスタムフック
 */
export function usePackageVulnIds(
  { pteamId, serviceId, packageId, relatedTicketStatus },
  options = {},
) {
  const skipByAuth = useSkipUntilAuthUserIsReady();
  return useGetPTeamVulnIdsTiedToServicePackageQuery(
    { pteamId, serviceId, packageId, relatedTicketStatus },
    {
      ...options,
      skip: skipByAuth || !pteamId || !serviceId || !packageId || options.skip,
    },
  );
}

/**
 * チケットカウント取得用カスタムフック
 */
export function usePackageTicketCounts(
  { pteamId, serviceId, packageId, relatedTicketStatus },
  options = {},
) {
  const skipByAuth = useSkipUntilAuthUserIsReady();
  return useGetPTeamTicketCountsTiedToServicePackageQuery(
    { pteamId, serviceId, packageId, relatedTicketStatus },
    {
      ...options,
      skip: skipByAuth || !pteamId || !serviceId || !packageId || options.skip,
    },
  );
}

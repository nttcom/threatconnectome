import { useSkipUntilAuthUserIsReady } from "../../hooks/auth.js";
import {
  useGetDependenciesQuery,
  useGetPTeamQuery,
  useGetPTeamVulnIdsTiedToServicePackageQuery,
  useGetPTeamTicketCountsTiedToServicePackageQuery,
} from "../../services/tcApi.js";

/**
 * Package ページ専用のAPIフック
 */

/**
 * 依存関係データ取得用カスタムフック
 */
export function usePackageDependencies(
  { pteamId, serviceId, packageId, offset, limit },
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

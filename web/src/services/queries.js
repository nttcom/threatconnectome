import { useSkipUntilAuthUserIsReady } from "../hooks/auth.js";

import {
  useGetDependenciesQuery,
  useGetPTeamQuery,
  useGetPTeamVulnIdsTiedToServicePackageQuery,
  useGetPTeamTicketCountsTiedToServicePackageQuery,
} from "./tcApi.js";

/**
 * RTK Query フックのラッパー
 *
 * 各フックに共通の認証チェックとバリデーションを自動的に適用します。
 *
 * このパターンは React Query メンテナーの TkDodo が推奨するベストプラクティスを
 * RTK Query に適用したものです。
 * @see https://tkdodo.eu/blog/practical-react-query#create-custom-hooks
 */

export function useGetDependencies({ pteamId, serviceId, packageId, offset, limit }, options = {}) {
  const skipByAuth = useSkipUntilAuthUserIsReady();
  return useGetDependenciesQuery(
    { pteamId, serviceId, packageId, offset, limit },
    {
      ...options,
      skip: skipByAuth || !pteamId || !serviceId || options.skip,
    },
  );
}

export function useGetPTeam(pteamId, options = {}) {
  const skipByAuth = useSkipUntilAuthUserIsReady();
  return useGetPTeamQuery(pteamId, {
    ...options,
    skip: skipByAuth || !pteamId || options.skip,
  });
}

export function useGetPTeamVulnIds(
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

export function useGetPTeamTicketCounts(
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

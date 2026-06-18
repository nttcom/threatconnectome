import { useParams, useSearchParams } from "react-router-dom";

/**
 * Custom hook to get page parameters (path params and query params)
 * Used across multiple pages: Package, Vulnerability, Status, etc.
 */
export function usePageParams() {
  const { packageVersionId } = useParams();
  const [searchParams] = useSearchParams();

  return {
    packageVersionId,
    pteamId: searchParams.get("pteamId"),
    serviceId: searchParams.get("serviceId"),
  };
}

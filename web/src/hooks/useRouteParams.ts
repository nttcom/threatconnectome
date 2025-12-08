import { useLocation, useParams } from "react-router-dom";

interface PageParams {
  packageId?: string;
  pteamId: string | null;
  serviceId: string | null;
  vulnId: string | null;
}

/**
 * ページで使用するパラメータ（パスパラメータとクエリパラメータ）を取得するカスタムフック
 * Package, Vulnerability, Status などの複数のページで使用される
 */
export function usePageParams(): PageParams {
  const urlParams = useParams<{ packageId?: string }>();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);

  return {
    packageId: urlParams.packageId,
    pteamId: queryParams.get("pteamId"),
    serviceId: queryParams.get("serviceId"),
    vulnId: queryParams.get("vulnId"),
  };
}

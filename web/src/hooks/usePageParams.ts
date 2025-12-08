import { useParams, useSearchParams } from "react-router-dom";

/**
 * ページで使用するパラメータ（パスパラメータとクエリパラメータ）を取得するカスタムフック
 * Package, Vulnerability, Status などの複数のページで使用される
 */
export function usePageParams() {
  const { packageId } = useParams();
  const [searchParams] = useSearchParams();

  return {
    packageId,
    pteamId: searchParams.get("pteamId"),
    serviceId: searchParams.get("serviceId"),
    vulnId: searchParams.get("vulnId"),
  };
}

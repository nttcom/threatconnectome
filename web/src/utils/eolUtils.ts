import type { PTeamEoLProductResponse, EoLProductResponse } from "../../types/types.gen.ts";

export const formatDate = (dateStr: string | null | undefined) => {
  if (!dateStr) return "Undecided";
  return new Date(dateStr).toLocaleDateString();
};

export const getLatestUpdateDate = (
  eolProducts: PTeamEoLProductResponse[] | EoLProductResponse[],
) => {
  const latestUpdateDate = eolProducts
    .flatMap((eolProduct) => eolProduct.eol_versions ?? [])
    .map((eol_version) => new Date(eol_version.updated_at))
    .reduce((latest, current) => (current > latest ? current : latest), new Date(0));
  const latestUpdate =
    latestUpdateDate > new Date(0) ? latestUpdateDate.toLocaleDateString() : "N/A";

  return latestUpdate;
};

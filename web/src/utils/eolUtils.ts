import type {
  PTeamEoLProductResponse,
  ProductCategoryEnum,
  EoLProductResponse,
} from "../../types/types.gen.ts";

export const EoLProductCategoryList: { value: ProductCategoryEnum; label: string }[] = [
  { value: "os", label: "OS" },
  { value: "runtime", label: "Runtime" },
  { value: "middleware", label: "Middleware" },
  { value: "package", label: "Package" },
];

export const getProductCategorybyValue = (value: string | null | undefined) => {
  const item = EoLProductCategoryList.find((item) => item.value === value);
  return item ? item.label : "N/A";
};

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

export const getDiffDays = (eolDateStr: string | null | undefined): number | null => {
  if (!eolDateStr) return null;
  const eolDate = new Date(eolDateStr);
  const now = new Date();

  const todayUtc = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
  const eolUtc = new Date(
    Date.UTC(eolDate.getUTCFullYear(), eolDate.getUTCMonth(), eolDate.getUTCDate()),
  );

  const diffTime = eolUtc.getTime() - todayUtc.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};

export const WARNING_THRESHOLD_DAYS = 180;

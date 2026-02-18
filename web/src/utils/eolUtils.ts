import type { ProductCategoryEnum } from "../../types/types.gen";
import { t } from "i18next";

export const WARNING_THRESHOLD_DAYS = 180;

export const getEoLProductCategoryList = (): { value: ProductCategoryEnum; label: string }[] => [
  { value: "os", label: t("eolUtils.productCategory.os", { ns: "utils" }) },
  { value: "runtime", label: t("eolUtils.productCategory.runtime", { ns: "utils" }) },
  { value: "middleware", label: t("eolUtils.productCategory.middleware", { ns: "utils" }) },
  { value: "package", label: t("eolUtils.productCategory.package", { ns: "utils" }) },
];

export const getProductCategorybyValue = (value: string | null | undefined) => {
  const list = getEoLProductCategoryList();
  const item = list.find((item) => item.value === value);
  return item ? item.label : t("eolUtils.productCategory.na", { ns: "utils" });
};

export const getFormatDate = (dateStr: string | null | undefined) => {
  if (!dateStr) return t("eolUtils.formatDate.undecided", { ns: "utils" });
  return new Date(dateStr).toLocaleDateString();
};

interface HasUpdatedAt {
  updated_at: string;
}

export const getLatestUpdateDate = (items: HasUpdatedAt[]): string => {
  const latestUpdateDate = items
    .map((item) => new Date(item.updated_at))
    .reduce((latest, current) => (current > latest ? current : latest), new Date(0));

  return latestUpdateDate > new Date(0) ? latestUpdateDate.toLocaleDateString() : "N/A";
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

// ---  Type definition ---
export type Status = "expired" | "warning" | "active" | "unknown";

export const getStatusLabel = (status: Status) => {
  switch (status) {
    case "expired":
      return t("eolUtils.status.expired", { ns: "utils" });
    case "warning":
      return t("eolUtils.status.warning", { ns: "utils" });
    case "active":
      return t("eolUtils.status.active", { ns: "utils" });
    case "unknown":
      return t("eolUtils.status.unknown", { ns: "utils" });
  }
};

export const getEolStatus = (eolDateStr: string | null | undefined) => {
  const diffDays = getDiffDays(eolDateStr);
  if (diffDays === null || diffDays === undefined) return "unknown";
  if (diffDays < 0) return "expired";
  if (diffDays <= WARNING_THRESHOLD_DAYS) return "warning";
  return "active";
};

export const getDiffText = (eolDateStr: string) => {
  const diffDays = getDiffDays(eolDateStr);

  if (diffDays === null || diffDays === undefined) return "-";
  if (diffDays < 0)
    return t("eolUtils.diffText.daysOver", { ns: "utils", days: Math.abs(diffDays) });
  if (diffDays === 0) return t("eolUtils.diffText.expiresToday", { ns: "utils" });
  return t("eolUtils.diffText.daysLeft", { ns: "utils", days: diffDays });
};

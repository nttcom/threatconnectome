import { t } from "i18next";

/**
 * Calculates the estimated analysis time based on the SBOM file size.
 * @param sizeInBytes - The size of the SBOM file in Bytes (B).
 * @returns The estimated processing time in minutes.
 */
export function calculateEstimateTimeFromSize(sizeInBytes: number): string {
  const estimateTime = calculateEstimateTimeFromSizeWithoutFormat(sizeInBytes);
  return _formatEstimatedTime(estimateTime);
}

export function calculateEstimateTimeFromSizeWithoutFormat(sizeInBytes: number): number {
  // Convert Bytes to Kilobytes to maintain consistency with the original regression model
  const sizeInKB = sizeInBytes / 1024;

  // Constants for the quadratic regression model (based on KB input): y = c0 + c1*x + c2*x^2
  const c0 = 0.0871; // Intercept (base overhead)
  const c1 = 2.47e-3; // Linear coefficient
  const c2 = 1.34e-7; // Quadratic coefficient for non-linear scaling

  return c0 + c1 * sizeInKB + c2 * Math.pow(sizeInKB, 2);
}

const _formatEstimatedTime = (totalMinutes: number): string => {
  let roundedMinutes = Math.max(1, Math.round(totalMinutes));
  if (roundedMinutes < 60) {
    return t("estimator.minutes", { ns: "utils", minutes: roundedMinutes });
  }

  const hours = Math.floor(roundedMinutes / 60);
  const minutes = roundedMinutes % 60;

  return t("estimator.hoursAndMinutes", { ns: "utils", hours: hours, minutes: minutes });
};

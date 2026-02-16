import { VulnResponse, VulnerablePackageResponse } from "../../types/types.gen";
import { t } from "i18next";

interface currentPackage {
  package_name: string;
  package_source_name?: string | null;
  vuln_matching_ecosystem: string;
}

export const createUpdateAction = (
  affectedVersions: Array<string>,
  fixedVersions: Array<string>,
  packageName: string,
) => {
  if (fixedVersions && fixedVersions.length > 0) {
    const fromBracketed =
      affectedVersions && affectedVersions.length > 0 ? `[${affectedVersions.join(", ")}]` : null;
    const toBracketed = `[${fixedVersions.join(", ")}]`;

    if (fromBracketed) {
      return t("vulnUtils.updateFromTo", {
        ns: "utils",
        package: packageName,
        from: fromBracketed,
        to: toBracketed,
      });
    }

    return t("vulnUtils.updateToVersion", {
      ns: "utils",
      package: packageName,
      to: toBracketed,
    });
  }

  return null;
};

export function getUpdateActions(vuln: VulnResponse) {
  const updateActions: string[] = [];
  if (vuln && Array.isArray(vuln.vulnerable_packages)) {
    vuln.vulnerable_packages.forEach((vulnerable_package) => {
      const updateAction = createUpdateAction(
        vulnerable_package.affected_versions,
        vulnerable_package.fixed_versions,
        vulnerable_package.affected_name,
      );
      if (updateAction != null) {
        updateActions.push(updateAction);
      }
    });
  }

  return updateActions;
}

export function findMatchedVulnPackage(
  vulnerable_packages: Array<VulnerablePackageResponse>,
  currentPackage: currentPackage,
) {
  const { package_source_name, package_name, vuln_matching_ecosystem } = currentPackage;
  return vulnerable_packages.find(
    (vulnerable_package) =>
      vulnerable_package.ecosystem === vuln_matching_ecosystem &&
      (vulnerable_package.affected_name === package_source_name ||
        vulnerable_package.affected_name === package_name),
  );
}

export function isValidCVEFormat(value: string) {
  const trimmedValue = value.trim();
  const CVE_PATTERN = /^CVE-\d{4}-\d{4,}$/;

  return !trimmedValue || CVE_PATTERN.test(trimmedValue);
}

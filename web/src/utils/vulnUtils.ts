import { VulnResponse, VulnerablePackageResponse } from "../../types/types.gen.ts";

interface currentPackage {
  package_name: string;
  package_source_name: string | null | undefined;
  vuln_matching_ecosystem: string;
}

export const createUpdateAction = (
  affectedVersions: Array<string>,
  fixedVersions: Array<string>,
  packageName: string,
) => {
  if (fixedVersions && fixedVersions.length > 0) {
    if (affectedVersions && affectedVersions.length > 0) {
      return `Update ${packageName} from [${affectedVersions.join(", ")}] to [${fixedVersions.join(", ")}]`;
    } else {
      return `Update ${packageName} to version [${fixedVersions.join(", ")}]`;
    }
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

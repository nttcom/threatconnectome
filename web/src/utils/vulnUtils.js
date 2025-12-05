export const createUpdateAction = (affectedVersions, fixedVersions, packageName) => {
  if (fixedVersions && fixedVersions.length > 0) {
    if (affectedVersions && affectedVersions.length > 0) {
      return `Update ${packageName} from [${affectedVersions.join(", ")}] to [${fixedVersions.join(", ")}]`;
    } else {
      return `Update ${packageName} to version [${fixedVersions.join(", ")}]`;
    }
  }

  return null;
};

export function getUpdateActions(vuln) {
  const updateActions = [];
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

  return updateActions;
}

export function findMatchedVulnPackage(vulnerable_packages, currentPackage) {
  const { package_source_name, package_name, vuln_matching_ecosystem } = currentPackage;
  return vulnerable_packages.find(
    (vulnerable_package) =>
      vulnerable_package.ecosystem === vuln_matching_ecosystem &&
      (vulnerable_package.affected_name === package_source_name ||
        vulnerable_package.affected_name === package_name),
  );
}

export function isValidCVEFormat(value) {
  const trimmedValue = value.trim();
  const CVE_PATTERN = /^CVE-\d{4}-\d{4,}$/;

  return !trimmedValue || CVE_PATTERN.test(trimmedValue);
}

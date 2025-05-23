import { pickParentTagName } from "./func";
import { parseVulnerableVersions, versionMatch } from "./versions";

export function pickAffectedVersions(vulnActions, packageName) {
  const versions = pickAffectedVersionsInner(vulnActions, packageName);

  const parentTagName = pickParentTagName(packageName);
  if (parentTagName == null) {
    if (versions.length == 0) {
      return ["?"];
    }
    return [...new Set(versions)].sort();
  }

  const paretntVersions = pickAffectedVersionsInner(vulnActions, parentTagName);
  if (versions.length == 0 && paretntVersions.length == 0) {
    return ["?"];
  }
  return [...new Set(versions.concat(paretntVersions))].sort();
}

function pickAffectedVersionsInner(vulnActions, packageName) {
  return vulnActions.reduce(
    (ret, action) => [...ret, ...(action.ext?.vulnerable_versions?.[packageName] ?? [])],
    [],
  );
}

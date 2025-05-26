import { pickParentTagName } from "./func";
import { parseVulnerableVersions, versionMatch } from "./versions";

function pickAffectedVersionsInner(vulnActions, packageName) {
  return vulnActions.reduce(
    (ret, action) => [...ret, ...(action.ext?.vulnerable_versions?.[packageName] ?? [])],
    [],
  );
}

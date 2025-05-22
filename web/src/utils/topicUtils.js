import { pickParentTagName } from "./func";
import { parseVulnerableVersions, versionMatch } from "./versions";

export function pickAffectedVersions(vulnActions, packageName) {
  const versions = pickAffectedVersionsInner(vulnActions, packageName);

  console.log("vulnActions : ", vulnActions);
  console.log("packageName : ", packageName);
  console.log("versions : ", versions);
  const parentTagName = pickParentTagName(packageName);
  // 親タグ名が存在しない場合の処理
  if (parentTagName == null) {
    if (versions.length == 0) {
      return ["?"];
    }
    return [...new Set(versions)].sort();
  }

  // 親タグ名が存在する場合の処理
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

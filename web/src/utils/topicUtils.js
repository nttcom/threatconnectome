import { pickParentTagName } from "./func";

export function pickAffectedVersions(topicActions, tagName) {
  const versions = pickAffectedVersionsInner(topicActions, tagName);

  const parentTagName = pickParentTagName(tagName);
  if (parentTagName == null) {
    if (versions.length == 0) {
      return ["?"];
    }
    return [...new Set(versions)].sort();
  }

  const paretntVersions = pickAffectedVersionsInner(topicActions, parentTagName);
  if (versions.length == 0 && paretntVersions.length == 0) {
    return ["?"];
  }
  return [...new Set(versions.concat(paretntVersions))].sort();
}

function pickAffectedVersionsInner(topicActions, tagName) {
  return topicActions.reduce(
    (ret, action) => [...ret, ...(action.ext?.vulnerable_versions?.[tagName] ?? [])],
    [],
  );
}

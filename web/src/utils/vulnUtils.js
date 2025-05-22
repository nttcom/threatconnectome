export const createActionText = (affectedVersion, fixedVersion, packageName) => {
  const action = {
    // Create action_id to make it common processing with manual registration action
    // This action_id is only used on the UI
    action_id: self.crypto.randomUUID(),
    action_type: "elimination",
    recommended: true,
  };

  if (affectedVersion && fixedVersion) {
    action.action = `Update ${packageName} from ${affectedVersion} to ${fixedVersion}`;
    return action;
  } else if (fixedVersion) {
    action.action = `Update ${packageName} to version ${fixedVersion}`;
    return action;
  }

  return null;
};

export function getActions(vuln, vulnActions) {
  const actionsByFixedVersions = [];
  vuln.vulnerable_packages.forEach((vulnerable_package) => {
    const actionText = createActionText(
      vulnerable_package.affected_versions.join(),
      vulnerable_package.fixed_versions.join(),
      vulnerable_package.name,
    );
    if (actionText != null) {
      actionsByFixedVersions.push(actionText);
    }
  });

  return [...actionsByFixedVersions, ...vulnActions];
}

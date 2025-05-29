export const createActionByFixedVersions = (affectedVersions, fixedVersions, packageName) => {
  const action = {
    // Create action_id to make it common processing with manual registration action
    // This action_id is only used on the UI
    action_id: self.crypto.randomUUID(),
    action_type: "elimination",
    recommended: true,
  };

  if (fixedVersions && fixedVersions.length > 0) {
    if (affectedVersions && affectedVersions.length > 0) {
      action.action = `Update ${packageName} from [${affectedVersions.join(", ")}] to [${fixedVersions.join(", ")}]`;
      return action;
    } else {
      action.action = `Update ${packageName} to version [${fixedVersions.join(", ")}]`;
      return action;
    }
  }

  return null;
};

export function getActions(vuln, vulnActions) {
  const actionsByFixedVersions = [];
  vuln.vulnerable_packages.forEach((vulnerable_package) => {
    const action = createActionByFixedVersions(
      vulnerable_package.affected_versions,
      vulnerable_package.fixed_versions,
      vulnerable_package.name,
    );
    if (action != null) {
      actionsByFixedVersions.push(action);
    }
  });

  return [...actionsByFixedVersions, ...vulnActions];
}

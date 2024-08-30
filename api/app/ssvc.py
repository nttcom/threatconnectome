from app import models


def calculate_ssvc_deployer_priority(
    threat: models.Threat,
) -> models.SSVCDeployerPriorityEnum | None:
    topic = threat.topic
    service = threat.dependency.service
    exploitation = topic.exploitation  # noqa: F841
    system_exposure = service.system_exposure  # noqa: F841
    automatable = topic.automatable  # noqa: F841
    mission_impact = calculate_mission_impact(threat.dependency)  # noqa: F841
    # TODO Calculation not implemented.

    if threat.topic.threat_impact == 1:
        ssvc_deployer_priority = models.SSVCDeployerPriorityEnum.IMMEDIATE
    elif threat.topic.threat_impact == 2:
        ssvc_deployer_priority = models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE
    elif threat.topic.threat_impact == 3:
        ssvc_deployer_priority = models.SSVCDeployerPriorityEnum.SCHEDULED
    elif threat.topic.threat_impact == 4:
        ssvc_deployer_priority = models.SSVCDeployerPriorityEnum.DEFER
    else:
        ssvc_deployer_priority = models.SSVCDeployerPriorityEnum.IMMEDIATE

    return ssvc_deployer_priority


def calculate_mission_impact(
    dependency: models.Dependency,
) -> models.MissionImpactEnum | None:
    if dependency and dependency.dependency_mission_impact:
        return dependency.dependency_mission_impact
    return dependency.service.service_mission_impact

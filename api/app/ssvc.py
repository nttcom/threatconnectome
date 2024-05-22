from app import models


def calculate_ssvc_deployer_priority(
    threat: models.Threat, dependency: models.Dependency | None
) -> models.SSVCDeployerPriorityEnum | None:
    topic = threat.topic
    service = threat.dependency.service
    exploitation = topic.exploitation
    exposure = service.exposure
    automatable = topic.automatable
    mission_impact = calculate_mission_impact(threat.dependency.service, dependency)
    safety_impact = topic.safety_impact
    # TODO Calculation not implemented.
    return (
        models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE
        if exploitation and exposure and automatable and mission_impact and safety_impact
        else models.SSVCDeployerPriorityEnum.DEFER
    )


def calculate_mission_impact(
    service: models.Service,
    dependency: models.Dependency | None,
) -> models.MissionImpactEnum | None:
    if dependency and dependency.dependency_mission_impact:
        return dependency.dependency_mission_impact
    return service.service_mission_impact

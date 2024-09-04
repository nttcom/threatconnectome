from app import models
from app.ssvc import deployer_data


def _get_automatable_value(automatable: models.AutomatableEnum) -> str:
    match automatable:
        case models.AutomatableEnum.YES:
            return "yes"
        case models.AutomatableEnum.NO:
            return "no"


def _get_exploitation_value(exploitation: models.ExploitationEnum) -> str:
    match exploitation:
        case models.ExploitationEnum.ACTIVE:
            return "active"
        case models.ExploitationEnum.PUBLIC_POC:
            return "poc"
        case models.ExploitationEnum.NONE:
            return "none"


def _get_system_exposure_value(system_exposure: models.SystemExposureEnum) -> str:
    match system_exposure:
        case models.SystemExposureEnum.OPEN:
            return "open"
        case models.SystemExposureEnum.CONTROLLED:
            return "controlled"
        case models.SystemExposureEnum.SMALL:
            return "small"


def _get_safety_impact_value(safety_impact: models.SafetyImpactEnum) -> str:
    match safety_impact:
        case models.SafetyImpactEnum.CATASTROPHIC:
            return "catastrophic"
        case models.SafetyImpactEnum.CRITICAL:
            return "critical"
        case models.SafetyImpactEnum.MARGINAL:
            return "marginal"
        case models.SafetyImpactEnum.NEGLIGIBLE:
            return "negligible"


def _get_mission_impact_value(mission_impact: models.MissionImpactEnum) -> str:
    match mission_impact:
        case models.MissionImpactEnum.MISSION_FAILURE:
            return "mission failure"
        case models.MissionImpactEnum.MEF_FAILURE:
            return "mef failure"
        case models.MissionImpactEnum.MEF_SUPPORT_CRIPPLED:
            return "crippled"
        case models.MissionImpactEnum.DEGRADED:
            return "degraded"


def _get_human_impact_value_dict() -> dict:
    return {
        "low": models.HumanImpactEnum.LOW,
        "medium": models.HumanImpactEnum.MEDIUM,
        "high": models.HumanImpactEnum.HIGH,
        "very high": models.HumanImpactEnum.VERY_HIGH,
    }


def _get_ssvc_priority_enum(ssvc_priority: str | None) -> models.SSVCDeployerPriorityEnum | None:
    if ssvc_priority is None:
        return None
    match ssvc_priority:
        case "defer":
            return models.SSVCDeployerPriorityEnum.DEFER
        case "scheduled":
            return models.SSVCDeployerPriorityEnum.SCHEDULED
        case "out-of-cycle":
            return models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE
        case "immediate":
            return models.SSVCDeployerPriorityEnum.IMMEDIATE
        case _:
            return None


def calculate_ssvc_priority_by_threat(
    threat: models.Threat,
) -> models.SSVCDeployerPriorityEnum | None:
    topic = threat.topic
    service = threat.dependency.service
    exploitation = topic.exploitation
    system_exposure = service.system_exposure
    automatable = topic.automatable
    mission_impact = calculate_mission_impact(threat.dependency)
    safety_impact = service.safety_impact
    human_impact = calculate_human_impact(safety_impact, mission_impact)
    return _calculate_ssvc_priority(exploitation, system_exposure, automatable, human_impact)


def calculate_mission_impact(
    dependency: models.Dependency,
) -> models.MissionImpactEnum:
    if dependency and dependency.dependency_mission_impact:
        return dependency.dependency_mission_impact
    return dependency.service.service_mission_impact


def calculate_human_impact(
    safety_impact: models.SafetyImpactEnum, mission_impact: models.MissionImpactEnum
) -> models.HumanImpactEnum | None:
    key = (
        _get_safety_impact_value(safety_impact),
        _get_mission_impact_value(mission_impact),
    )
    human_impact_dict = deployer_data.get_human_impact_dict()
    human_impact_value = human_impact_dict.get(key)
    return _get_human_impact_value_dict().get(human_impact_value)


def _calculate_ssvc_priority(
    exploitation: models.ExploitationEnum,
    system_exposure: models.SystemExposureEnum,
    automatable: models.AutomatableEnum,
    human_impact: models.HumanImpactEnum | None,
) -> models.SSVCDeployerPriorityEnum | None:
    human_impact_value = [
        human_impact_value
        for human_impact_value, human_impact_enum in _get_human_impact_value_dict().items()
        if human_impact_enum == human_impact
    ][0]
    key = (
        _get_exploitation_value(exploitation),
        _get_system_exposure_value(system_exposure),
        _get_automatable_value(automatable),
        human_impact_value,
    )
    ssvc_priority_dict = deployer_data.get_ssvc_priority_dict()
    return _get_ssvc_priority_enum(ssvc_priority_dict.get(key))

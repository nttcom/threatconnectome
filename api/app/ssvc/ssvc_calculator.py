from app import models
from app.ssvc import deployer_data


def get_automatable_value(automatable: models.AutomatableEnum) -> str:
    match automatable:
        case models.AutomatableEnum.YES:
            return "yes"
        case models.AutomatableEnum.NO:
            return "no"


def get_exploitation_value(exploitation: models.ExploitationEnum) -> str:
    match exploitation:
        case models.ExploitationEnum.ACTIVE:
            return "active"
        case models.ExploitationEnum.PUBLIC_POC:
            return "poc"
        case models.ExploitationEnum.NONE:
            return "none"


def get_system_exposure_value(system_exposure: models.SystemExposureEnum) -> str:
    match system_exposure:
        case models.SystemExposureEnum.OPEN:
            return "open"
        case models.SystemExposureEnum.CONTROLLED:
            return "controlled"
        case models.SystemExposureEnum.SMALL:
            return "small"


def get_safety_impact_value(safety_impact: models.SafetyImpactEnum) -> str:
    match safety_impact:
        case models.SafetyImpactEnum.CATASTROPHIC:
            return "catastrophic"
        case models.SafetyImpactEnum.CRITICAL:
            return "critical"
        case models.SafetyImpactEnum.MARGINAL:
            return "marginal"
        case models.SafetyImpactEnum.NEGLIGIBLE:
            return "negligible"


def get_mission_impact_value(mission_impact: models.MissionImpactEnum) -> str:
    match mission_impact:
        case models.MissionImpactEnum.MISSION_FAILURE:
            return "mission failure"
        case models.MissionImpactEnum.MEF_FAILURE:
            return "mef failure"
        case models.MissionImpactEnum.MEF_SUPPORT_CRIPPLED:
            return "crippled"
        case models.MissionImpactEnum.DEGRADED:
            return "degraded"


def get_ssvc_priority_enum(ssvc_priority: str | None) -> models.SSVCDeployerPriorityEnum | None:
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


def calculate_ssvc_deployer_priority(
    threat: models.Threat,
) -> models.SSVCDeployerPriorityEnum | None:
    topic = threat.topic
    service = threat.dependency.service
    exploitation = topic.exploitation
    system_exposure = service.system_exposure
    automatable = topic.automatable
    mission_impact = service.service_mission_impact
    safety_impact = service.safety_impact
    human_impact = calculate_human_impact(safety_impact, mission_impact)
    return calculate_ssvc_priority(exploitation, system_exposure, automatable, human_impact)


def calculate_human_impact(
    situated_safety_impact: models.SafetyImpactEnum, mission_impact: models.MissionImpactEnum
) -> str | None:
    key = (
        get_safety_impact_value(situated_safety_impact),
        get_mission_impact_value(mission_impact),
    )
    human_impact_dict = deployer_data.get_human_impact_dict()
    if key in human_impact_dict.keys():
        return human_impact_dict[key]
    return None


def calculate_ssvc_priority(
    exploitation: models.ExploitationEnum,
    system_exposure: models.SystemExposureEnum,
    automatable: models.AutomatableEnum,
    human_impact: str | None,
) -> models.SSVCDeployerPriorityEnum | None:
    key = (
        get_exploitation_value(exploitation),
        get_system_exposure_value(system_exposure),
        get_automatable_value(automatable),
        human_impact,
    )
    ssvc_priority_dict = deployer_data.get_ssvc_priority_dict()
    if key in ssvc_priority_dict.keys():
        return get_ssvc_priority_enum(ssvc_priority_dict[key])
    return None

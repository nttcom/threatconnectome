import pytest

from app import models
from app.ssvc import ssvc_calculator


@pytest.mark.parametrize(
    "safety_impact, mission_impact, expected_human_impact",
    [
        # https://certcc.github.io/SSVC/howto/deployer_tree/#table-of-values
        (
            models.SafetyImpactEnum.NEGLIGIBLE,
            models.MissionImpactEnum.DEGRADED,
            models.HumanImpactEnum.LOW,
        ),
        (
            models.SafetyImpactEnum.NEGLIGIBLE,
            models.MissionImpactEnum.MEF_SUPPORT_CRIPPLED,
            models.HumanImpactEnum.LOW,
        ),
        (
            models.SafetyImpactEnum.NEGLIGIBLE,
            models.MissionImpactEnum.MEF_FAILURE,
            models.HumanImpactEnum.MEDIUM,
        ),
        (
            models.SafetyImpactEnum.MARGINAL,
            models.MissionImpactEnum.DEGRADED,
            models.HumanImpactEnum.MEDIUM,
        ),
        (
            models.SafetyImpactEnum.MARGINAL,
            models.MissionImpactEnum.MEF_SUPPORT_CRIPPLED,
            models.HumanImpactEnum.MEDIUM,
        ),
        (
            models.SafetyImpactEnum.CRITICAL,
            models.MissionImpactEnum.DEGRADED,
            models.HumanImpactEnum.HIGH,
        ),
        (
            models.SafetyImpactEnum.CRITICAL,
            models.MissionImpactEnum.MEF_SUPPORT_CRIPPLED,
            models.HumanImpactEnum.HIGH,
        ),
        (
            models.SafetyImpactEnum.CRITICAL,
            models.MissionImpactEnum.MEF_FAILURE,
            models.HumanImpactEnum.HIGH,
        ),
        (
            models.SafetyImpactEnum.MARGINAL,
            models.MissionImpactEnum.MEF_FAILURE,
            models.HumanImpactEnum.HIGH,
        ),
        (
            models.SafetyImpactEnum.CATASTROPHIC,
            models.MissionImpactEnum.DEGRADED,
            models.HumanImpactEnum.VERY_HIGH,
        ),
        (
            models.SafetyImpactEnum.CATASTROPHIC,
            models.MissionImpactEnum.MEF_SUPPORT_CRIPPLED,
            models.HumanImpactEnum.VERY_HIGH,
        ),
        (
            models.SafetyImpactEnum.CATASTROPHIC,
            models.MissionImpactEnum.MEF_FAILURE,
            models.HumanImpactEnum.VERY_HIGH,
        ),
        (
            models.SafetyImpactEnum.NEGLIGIBLE,
            models.MissionImpactEnum.MISSION_FAILURE,
            models.HumanImpactEnum.VERY_HIGH,
        ),
        (
            models.SafetyImpactEnum.MARGINAL,
            models.MissionImpactEnum.MISSION_FAILURE,
            models.HumanImpactEnum.VERY_HIGH,
        ),
        (
            models.SafetyImpactEnum.CRITICAL,
            models.MissionImpactEnum.MISSION_FAILURE,
            models.HumanImpactEnum.VERY_HIGH,
        ),
        (
            models.SafetyImpactEnum.CATASTROPHIC,
            models.MissionImpactEnum.MISSION_FAILURE,
            models.HumanImpactEnum.VERY_HIGH,
        ),
    ],
)
def test_calculate_human_impact(
    safety_impact: models.SafetyImpactEnum,
    mission_impact: models.MissionImpactEnum,
    expected_human_impact: models.HumanImpactEnum | None,
):
    human_impact = ssvc_calculator._calculate_human_impact(safety_impact, mission_impact)
    assert human_impact == expected_human_impact


@pytest.mark.parametrize(
    "exploitation, system_exposure, automatable, human_impact, expected_ssvc_priority",
    [
        # https://certcc.github.io/SSVC/howto/deployer_tree/#table-of-values
        # row: 1
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.DEFER,
        ),
        # row: 2
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.DEFER,
        ),
        # row: 3
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 4
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 5
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.DEFER,
        ),
        # row: 6
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 7
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 8
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 9
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.DEFER,
        ),
        # row: 10
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 11
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 12
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 13
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 14
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 15
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 16
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 17
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.DEFER,
        ),
        # row: 18
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 19
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 20
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 21
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 22
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 23
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 24
        (
            models.ExploitationEnum.NONE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 25
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.DEFER,
        ),
        # row: 26
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 27
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 28
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 29
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 30
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 31
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 32
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 33
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.DEFER,
        ),
        # row: 34
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 35
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 36
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 37
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 38
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 39
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 40
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 41
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 42
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 43
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 44
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 45
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 46
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 47
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 48
        (
            models.ExploitationEnum.PUBLIC_POC,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 49
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 50
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 51
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 52
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 53
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 54
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 55
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 56
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.SMALL,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 57
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 58
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 59
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 60
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 61
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 62
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 63
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 64
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.CONTROLLED,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 65
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
        ),
        # row: 66
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 67
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 68
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.NO,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.IMMEDIATE,
        ),
        # row: 69
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.LOW,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 70
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.MEDIUM,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        ),
        # row: 71
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.HIGH,
            models.SSVCDeployerPriorityEnum.IMMEDIATE,
        ),
        # row: 72
        (
            models.ExploitationEnum.ACTIVE,
            models.SystemExposureEnum.OPEN,
            models.AutomatableEnum.YES,
            models.HumanImpactEnum.VERY_HIGH,
            models.SSVCDeployerPriorityEnum.IMMEDIATE,
        ),
    ],
)
def test_calculate_ssvc_priority(
    exploitation: models.ExploitationEnum,
    system_exposure: models.SystemExposureEnum,
    automatable: models.AutomatableEnum,
    human_impact: models.HumanImpactEnum,
    expected_ssvc_priority: models.SSVCDeployerPriorityEnum,
):
    ssvc_priority = ssvc_calculator._calculate_ssvc_priority(
        exploitation, system_exposure, automatable, human_impact
    )
    assert ssvc_priority == expected_ssvc_priority

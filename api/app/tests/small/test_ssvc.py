import pytest

from app import models, ssvc


@pytest.mark.parametrize(
    "service_mission_impact, dependency_mission_impact, expected_mission_impact",
    [
        # Prioritize dependency_mission_impact.
        (
            models.MissionImpactEnum.CRIPPLED,
            models.MissionImpactEnum.DEGRADED,
            models.MissionImpactEnum.DEGRADED,
        ),
        # If dependency_mission_impact is None, service_mission_impact is enabled.
        (
            models.MissionImpactEnum.CRIPPLED,
            None,
            models.MissionImpactEnum.CRIPPLED,
        ),
        # The models.MissionImpactEnum.NONE is considered specified.
        (
            models.MissionImpactEnum.DEGRADED,
            models.MissionImpactEnum.NONE,
            models.MissionImpactEnum.NONE,
        ),
        (
            models.MissionImpactEnum.NONE,
            models.MissionImpactEnum.DEGRADED,
            models.MissionImpactEnum.DEGRADED,
        ),
    ],
)
def test_calculate_mission_impact(
    service_mission_impact: models.MissionImpactEnum,
    dependency_mission_impact: models.MissionImpactEnum,
    expected_mission_impact: models.MissionImpactEnum,
):
    service = models.Service(
        pteam_id="pteam_id",
        service_mission_impact=service_mission_impact,
    )
    dependency = models.Dependency(
        service_id="service_id",
        tag_id="tag_id",
        dependency_mission_impact=dependency_mission_impact,
    )
    service.dependencies.append(dependency)

    mission_impact = ssvc.calculate_mission_impact(dependency)
    assert mission_impact == expected_mission_impact

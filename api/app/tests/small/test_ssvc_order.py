from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app import models
from app.business.ssvc_business import _create_vuln_ids_summary


def test_ssvc_priority_enum_comparison_with_different_type():
    with pytest.raises(TypeError):
        assert models.SSVCDeployerPriorityEnum.DEFER < 3
    with pytest.raises(TypeError):
        assert models.SSVCDeployerPriorityEnum.DEFER > 3
    with pytest.raises(TypeError):
        assert models.SSVCDeployerPriorityEnum.DEFER <= 3
    with pytest.raises(TypeError):
        assert models.SSVCDeployerPriorityEnum.DEFER <= 3


[_immediate, _out_of_cycle, _scheduled, _defer] = list(models.SSVCDeployerPriorityEnum)


@pytest.mark.parametrize("right", [_immediate, _out_of_cycle, _scheduled, _defer])
@pytest.mark.parametrize("operator", [">", ">=", "==", "!=", "<=", "<"])
@pytest.mark.parametrize("left", [_immediate, _out_of_cycle, _scheduled, _defer])
def test_comparison_operators(left, right, operator):
    expected_order = {_immediate: 1, _out_of_cycle: 2, _scheduled: 3, _defer: 4}
    left_order = expected_order[left]
    right_order = expected_order[right]

    operators_equal = {">=", "==", "<="}
    operators_small = {"<", "<=", "!="}
    operators_large = {">", ">=", "!="}

    if left_order == right_order:
        expected_true_operators = operators_equal
    elif left_order < right_order:
        expected_true_operators = operators_small
    else:
        expected_true_operators = operators_large

    expected = operator in expected_true_operators
    assert eval(f"left {operator} right") is expected


def test_vuln_ids_summary_sorts_ssvc_priority_from_worst_to_best():
    # Given
    now = datetime.now(timezone.utc)
    defer_vuln_id = uuid4()
    immediate_vuln_id = uuid4()
    out_of_cycle_vuln_id = uuid4()
    scheduled_vuln_id = uuid4()

    vuln_ids_dict = {
        defer_vuln_id: {
            "highest_ssvc_priority": models.SSVCDeployerPriorityEnum.DEFER,
            "vuln_updated_at": now,
            "vuln_id": defer_vuln_id,
        },
        immediate_vuln_id: {
            "highest_ssvc_priority": models.SSVCDeployerPriorityEnum.IMMEDIATE,
            "vuln_updated_at": now,
            "vuln_id": immediate_vuln_id,
        },
        out_of_cycle_vuln_id: {
            "highest_ssvc_priority": models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
            "vuln_updated_at": now,
            "vuln_id": out_of_cycle_vuln_id,
        },
        scheduled_vuln_id: {
            "highest_ssvc_priority": models.SSVCDeployerPriorityEnum.SCHEDULED,
            "vuln_updated_at": now,
            "vuln_id": scheduled_vuln_id,
        },
    }

    # When
    summary = _create_vuln_ids_summary(vuln_ids_dict)

    # Then
    assert summary["vuln_ids"] == [
        immediate_vuln_id,
        out_of_cycle_vuln_id,
        scheduled_vuln_id,
        defer_vuln_id,
    ]

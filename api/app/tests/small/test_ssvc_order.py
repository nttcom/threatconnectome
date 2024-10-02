import pytest

from app import models


def test_ssvc_priority_enum_comparison():
    assert models.SSVCDeployerPriorityEnum.DEFER == models.SSVCDeployerPriorityEnum.DEFER
    assert models.SSVCDeployerPriorityEnum.DEFER != models.SSVCDeployerPriorityEnum.SCHEDULED
    assert models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE < models.SSVCDeployerPriorityEnum.SCHEDULED
    assert models.SSVCDeployerPriorityEnum.SCHEDULED <= models.SSVCDeployerPriorityEnum.DEFER
    assert models.SSVCDeployerPriorityEnum.DEFER > models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE
    assert models.SSVCDeployerPriorityEnum.DEFER >= models.SSVCDeployerPriorityEnum.IMMEDIATE


def test_ssvc_priority_enum_comparison_with_different_type():
    with pytest.raises(TypeError):
        assert models.SSVCDeployerPriorityEnum.DEFER < 3
    with pytest.raises(TypeError):
        assert models.SSVCDeployerPriorityEnum.DEFER > 3
    with pytest.raises(TypeError):
        assert models.SSVCDeployerPriorityEnum.DEFER <= 3
    with pytest.raises(TypeError):
        assert models.SSVCDeployerPriorityEnum.DEFER <= 3


@pytest.mark.parametrize(
    "ssvc_priorityA, ssvc_priorityB, expected",
    [
        (
            models.SSVCDeployerPriorityEnum.DEFER,
            models.SSVCDeployerPriorityEnum.DEFER,
            True,
        ),
        (
            models.SSVCDeployerPriorityEnum.DEFER,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
            False,
        ),
        (
            models.SSVCDeployerPriorityEnum.DEFER,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
            False,
        ),
        (
            models.SSVCDeployerPriorityEnum.DEFER,
            models.SSVCDeployerPriorityEnum.IMMEDIATE,
            False,
        ),
        (
            models.SSVCDeployerPriorityEnum.SCHEDULED,
            models.SSVCDeployerPriorityEnum.DEFER,
            True,
        ),
        (
            models.SSVCDeployerPriorityEnum.SCHEDULED,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
            True,
        ),
        (
            models.SSVCDeployerPriorityEnum.SCHEDULED,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
            False,
        ),
        (
            models.SSVCDeployerPriorityEnum.SCHEDULED,
            models.SSVCDeployerPriorityEnum.IMMEDIATE,
            False,
        ),
        (
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
            models.SSVCDeployerPriorityEnum.DEFER,
            True,
        ),
        (
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
            True,
        ),
        (
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
            True,
        ),
        (
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
            models.SSVCDeployerPriorityEnum.IMMEDIATE,
            False,
        ),
        (
            models.SSVCDeployerPriorityEnum.IMMEDIATE,
            models.SSVCDeployerPriorityEnum.DEFER,
            True,
        ),
        (
            models.SSVCDeployerPriorityEnum.IMMEDIATE,
            models.SSVCDeployerPriorityEnum.SCHEDULED,
            True,
        ),
        (
            models.SSVCDeployerPriorityEnum.IMMEDIATE,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
            True,
        ),
        (
            models.SSVCDeployerPriorityEnum.IMMEDIATE,
            models.SSVCDeployerPriorityEnum.IMMEDIATE,
            True,
        ),
    ],
)
def test_ssvc_priority_enum_le(ssvc_priorityA, ssvc_priorityB, expected):
    assert (ssvc_priorityA <= ssvc_priorityB) == expected


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

import unicodedata

from app import models


def count_ssvc_priority_from_summary(tags_summary: list[dict]):
    ssvc_priority_count: dict[models.SSVCDeployerPriorityEnum, int] = {
        priority: 0 for priority in list(models.SSVCDeployerPriorityEnum)
    }
    for tag_summary in tags_summary:
        ssvc_priority_count[
            tag_summary["ssvc_priority"] or models.SSVCDeployerPriorityEnum.DEFER
        ] += 1
    return ssvc_priority_count


def count_full_width_and_half_width_characters(string: str) -> int:
    count: int = 0
    for char in string:
        if unicodedata.east_asian_width(char) in "WFA":
            count += 2
        else:
            count += 1

    return count

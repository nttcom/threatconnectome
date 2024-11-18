from uuid import UUID

from app import models


def _sum_ssvc_priority_count(topic_ids: list[str], topic_ids_dict: dict, count_key: str) -> dict:
    immediate = models.SSVCDeployerPriorityEnum.IMMEDIATE.value
    out_of_cycle = models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE.value
    scheduled = models.SSVCDeployerPriorityEnum.SCHEDULED.value
    defer = models.SSVCDeployerPriorityEnum.DEFER.value
    sum_threat_impact_count = {immediate: 0, out_of_cycle: 0, scheduled: 0, defer: 0}
    for topic_id in topic_ids:
        current_count = topic_ids_dict[topic_id][count_key]
        sum_threat_impact_count[immediate] += current_count[immediate]
        sum_threat_impact_count[out_of_cycle] += current_count[out_of_cycle]
        sum_threat_impact_count[scheduled] += current_count[scheduled]
        sum_threat_impact_count[defer] += current_count[defer]
    return sum_threat_impact_count


def get_topic_ids_summary_by_service_id_and_tag_id(
    service: models.Service,
    tag_id: UUID | str,
) -> dict:
    topic_ids_dict: dict = {}
    _completed = models.TopicStatusType.completed
    immediate = models.SSVCDeployerPriorityEnum.IMMEDIATE.value
    out_of_cycle = models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE.value
    scheduled = models.SSVCDeployerPriorityEnum.SCHEDULED.value
    defer = models.SSVCDeployerPriorityEnum.DEFER.value

    for dependency in service.dependencies:
        if dependency.tag_id != str(tag_id):
            continue
        for threat in dependency.threats:
            if not threat.ticket:
                continue
            ssvc_priority = (
                threat.ticket.ssvc_deployer_priority or models.SSVCDeployerPriorityEnum.DEFER
            )
            if (tmp_topic_ids_dict := topic_ids_dict.get(threat.topic_id)) is None:
                tmp_topic_ids_dict = {
                    "topic_id": threat.topic_id,
                    "highest_ssvc_priority": ssvc_priority,
                    "topic_updated_at": threat.topic.updated_at,
                    "is_solved": True,
                    "solved_ssvc_priority_count": {
                        immediate: 0,
                        out_of_cycle: 0,
                        scheduled: 0,
                        defer: 0,
                    },
                    "unsolved_ssvc_priority_count": {
                        immediate: 0,
                        out_of_cycle: 0,
                        scheduled: 0,
                        defer: 0,
                    },
                }
                topic_ids_dict[threat.topic_id] = tmp_topic_ids_dict
            if threat.ticket.ticket_status.topic_status == _completed:
                tmp_topic_ids_dict["solved_ssvc_priority_count"][ssvc_priority.value] += 1
            else:
                tmp_topic_ids_dict["unsolved_ssvc_priority_count"][ssvc_priority.value] += 1
                tmp_topic_ids_dict["is_solved"] = False

    # Sort topic_id according to threat_impact and updated_at
    topic_ids_sorted = sorted(
        topic_ids_dict.values(),
        key=lambda x: (
            x["highest_ssvc_priority"],
            -(_dt.timestamp() if (_dt := x["topic_updated_at"]) else 0),
        ),
    )
    solved_topic_ids = list(
        map(lambda item: item["topic_id"], filter(lambda item: item["is_solved"], topic_ids_sorted))
    )
    unsolved_topic_ids = list(
        map(
            lambda item: item["topic_id"],
            filter(lambda item: not item["is_solved"], topic_ids_sorted),
        )
    )
    # gen summary
    topic_ids_summary: dict[str, dict] = {
        "solved": {
            "topic_ids": solved_topic_ids,
            "ssvc_priority_count": _sum_ssvc_priority_count(
                solved_topic_ids, topic_ids_dict, "solved_ssvc_priority_count"
            ),
        },
        "unsolved": {
            "topic_ids": unsolved_topic_ids,
            "ssvc_priority_count": _sum_ssvc_priority_count(
                unsolved_topic_ids, topic_ids_dict, "unsolved_ssvc_priority_count"
            ),
        },
    }
    return topic_ids_summary

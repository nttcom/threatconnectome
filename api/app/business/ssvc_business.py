from uuid import UUID

from app import models


def _sum_ssvc_priority_count(topic_ids: list[str], topic_ids_dict: dict, count_key: str) -> dict:
    immediate = models.SSVCDeployerPriorityEnum.IMMEDIATE.value
    out_of_cycle = models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE.value
    scheduled = models.SSVCDeployerPriorityEnum.SCHEDULED.value
    defer = models.SSVCDeployerPriorityEnum.DEFER.value
    sum_ssvc_priority_count = {immediate: 0, out_of_cycle: 0, scheduled: 0, defer: 0}
    for topic_id in topic_ids:
        current_count = topic_ids_dict[topic_id][count_key]
        sum_ssvc_priority_count[immediate] += current_count[immediate]
        sum_ssvc_priority_count[out_of_cycle] += current_count[out_of_cycle]
        sum_ssvc_priority_count[scheduled] += current_count[scheduled]
        sum_ssvc_priority_count[defer] += current_count[defer]
    return sum_ssvc_priority_count


def get_vuln_ids_summary_by_service_id_and_package_id(
    pteam: models.PTeam,
    service: models.Service | None,
    package_id: UUID | str | None,
    related_ticket_status: str | None,
) -> dict:
    vuln_ids_dict: dict = {}

    if service is None:
        for _service in pteam.services:
            _update_vuln_ids_from_dependencies(
                _service, package_id, related_ticket_status, vuln_ids_dict
            )
    else:
        _update_vuln_ids_from_dependencies(
            service, package_id, related_ticket_status, vuln_ids_dict
        )

    # Sort vuln_id according to highest_ssvc_priority and updated_at
    vuln_ids_sorted = sorted(
        vuln_ids_dict.values(),
        key=lambda x: (
            x["highest_ssvc_priority"],
            -(_dt.timestamp() if (_dt := x["vuln_updated_at"]) else 0),
        ),
    )
    vuln_ids = list(map(lambda item: item["vuln_id"], vuln_ids_sorted))

    # gen summary
    vuln_ids_summary: dict[str, list] = {
        "vuln_ids": vuln_ids,
    }
    return vuln_ids_summary


def _update_vuln_ids_from_dependencies(
    service: models.Service,
    package_id: UUID | str | None,
    related_ticket_status: str | None,
    vuln_ids_dict: dict,
):
    _completed = models.TopicStatusType.completed

    for dependency in service.dependencies:
        if package_id and dependency.package_version.package_id != str(package_id):
            continue
        for ticket in dependency.tickets:
            if not ticket:
                continue

            ssvc_priority = ticket.ssvc_deployer_priority or models.SSVCDeployerPriorityEnum.DEFER

            if (
                related_ticket_status == "solved"
                and ticket.ticket_status.topic_status == _completed
            ):
                _update_vuln_ids_dict(vuln_ids_dict, ticket, ssvc_priority)
            elif (
                related_ticket_status == "unsolved"
                and ticket.ticket_status.topic_status != _completed
            ):
                _update_vuln_ids_dict(vuln_ids_dict, ticket, ssvc_priority)
            elif related_ticket_status is None:
                _update_vuln_ids_dict(vuln_ids_dict, ticket, ssvc_priority)


def _update_vuln_ids_dict(
    vuln_ids_dict: dict, ticket: models.Ticket, ssvc_priority: models.SSVCDeployerPriorityEnum
):
    if (tmp_vuln_ids_dict := vuln_ids_dict.get(ticket.threat.vuln_id)) is None:
        tmp_vuln_ids_dict = {
            "vuln_id": ticket.threat.vuln_id,
            "highest_ssvc_priority": ssvc_priority,
            "vuln_updated_at": ticket.threat.vuln.updated_at,
        }
        vuln_ids_dict[ticket.threat.vuln_id] = tmp_vuln_ids_dict

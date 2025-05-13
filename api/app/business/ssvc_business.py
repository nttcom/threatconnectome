from uuid import UUID

from app import models


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

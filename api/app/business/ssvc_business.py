from uuid import UUID

from sqlalchemy.orm import Session

from app import models
from app.business import dependency_business


def get_vuln_ids_summary_by_pteam_and_package_id(
    db: Session,
    pteam: models.PTeam,
    package_id: UUID | str | None,
    related_ticket_status: str | None,
) -> dict:
    vuln_ids_dict: dict = {}

    for _service in pteam.services:
        temp_vuln_ids_dict = _get_vuln_ids_dict_by_service(
            db, _service, package_id, related_ticket_status
        )
        for vuln_id, vuln_info in temp_vuln_ids_dict.items():
            if vuln_id not in vuln_ids_dict:
                vuln_ids_dict[vuln_id] = vuln_info

    return _create_vuln_ids_summary(vuln_ids_dict)


def get_vuln_ids_summary_by_service_and_package_id(
    db: Session,
    service: models.Service,
    package_id: UUID | str | None,
    related_ticket_status: str | None,
) -> dict:
    vuln_ids_dict: dict = _get_vuln_ids_dict_by_service(
        db, service, package_id, related_ticket_status
    )

    return _create_vuln_ids_summary(vuln_ids_dict)


def _get_vuln_ids_dict_by_service(
    db: Session,
    service: models.Service,
    package_id: UUID | str | None,
    related_ticket_status: str | None,
) -> dict:
    _completed = models.TicketHandlingStatusType.completed
    vuln_ids_dict = {}
    dependencies = dependency_business.get_dependencies_by_service(db, service, package_id)

    for dependency in dependencies:
        for ticket in dependency.tickets:
            if related_ticket_status == "solved":
                valid = ticket.ticket_status.ticket_handling_status == _completed
            elif related_ticket_status == "unsolved":
                valid = ticket.ticket_status.ticket_handling_status != _completed
            else:
                valid = True

            ssvc_priority = ticket.ssvc_deployer_priority or models.SSVCDeployerPriorityEnum.DEFER

            if ticket.threat.vuln_id not in vuln_ids_dict:
                vuln_ids_dict[ticket.threat.vuln_id] = {
                    "valid": valid,
                    "highest_ssvc_priority": ssvc_priority,
                    "vuln_updated_at": ticket.threat.vuln.updated_at,
                }
            else:
                vuln_info = vuln_ids_dict[ticket.threat.vuln_id]

                vuln_info["valid"] = vuln_info["valid"] or valid

                if vuln_info["highest_ssvc_priority"] > ssvc_priority:
                    vuln_info["highest_ssvc_priority"] = ssvc_priority

    for vuln_id in list(vuln_ids_dict.keys()):
        vuln_info = vuln_ids_dict[vuln_id]
        if not vuln_info["valid"]:
            del vuln_ids_dict[vuln_id]
        else:
            del vuln_info["valid"]
            vuln_info["vuln_id"] = vuln_id

    return vuln_ids_dict


def _create_vuln_ids_summary(vuln_ids_dict: dict) -> dict:
    # Sort vuln_id according to highest_ssvc_priority and updated_at
    vuln_ids_sorted = sorted(
        vuln_ids_dict.values(),
        key=lambda x: (
            x["highest_ssvc_priority"].value,
            -(_dt.timestamp() if (_dt := x["vuln_updated_at"]) else 0),
        ),
    )
    vuln_ids = list(map(lambda item: item["vuln_id"], vuln_ids_sorted))

    # gen summary
    vuln_ids_summary: dict[str, list] = {
        "vuln_ids": vuln_ids,
    }
    return vuln_ids_summary


def get_ticket_counts_summary_by_pteam_and_package_id(
    db: Session,
    pteam: models.PTeam,
    package_id: UUID | str | None,
    related_ticket_status: str | None,
):
    ticket_counts_dict: dict = _create_initial_ticket_counts_dict()

    for _service in pteam.services:
        temp_ticket_counts_dict: dict = _get_ticket_counts_by_service(
            db, _service, package_id, related_ticket_status
        )
        for ssvc_priority in models.SSVCDeployerPriorityEnum:
            ticket_counts_dict[ssvc_priority.value] += temp_ticket_counts_dict[ssvc_priority.value]

    # gen summary
    ticket_counts_summary: dict[str, dict] = {
        "ssvc_priority_count": ticket_counts_dict,
    }
    return ticket_counts_summary


def get_ticket_counts_summary_by_service_and_package_id(
    db: Session,
    service: models.Service,
    package_id: UUID | str | None,
    related_ticket_status: str | None,
):
    ticket_counts_dict: dict = _get_ticket_counts_by_service(
        db, service, package_id, related_ticket_status
    )

    # gen summary
    ticket_counts_summary: dict[str, dict] = {
        "ssvc_priority_count": ticket_counts_dict,
    }
    return ticket_counts_summary


def _get_ticket_counts_by_service(
    db: Session,
    service: models.Service,
    package_id: UUID | str | None,
    related_ticket_status: str | None,
) -> dict:
    vuln_ids_dict = {}
    _completed = models.TicketHandlingStatusType.completed

    dependencies = dependency_business.get_dependencies_by_service(db, service, package_id)
    for dependency in dependencies:
        for ticket in dependency.tickets:
            ssvc_priority = ticket.ssvc_deployer_priority or models.SSVCDeployerPriorityEnum.DEFER

            if related_ticket_status == "solved":
                valid = ticket.ticket_status.ticket_handling_status == _completed
            elif related_ticket_status == "unsolved":
                valid = ticket.ticket_status.ticket_handling_status != _completed
            else:
                valid = True

            if ticket.threat.vuln_id not in vuln_ids_dict:
                vuln_ids_dict[ticket.threat.vuln_id] = {
                    "vuln_id": ticket.threat.vuln_id,
                    "ssvc_priority_list": [ssvc_priority],
                    "valid": valid,
                }
            else:
                vuln_ids_dict[ticket.threat.vuln_id]["ssvc_priority_list"].append(ssvc_priority)
                vuln_ids_dict[ticket.threat.vuln_id]["valid"] = (
                    vuln_ids_dict[ticket.threat.vuln_id]["valid"] or valid
                )

    ticket_counts_dict: dict = _create_initial_ticket_counts_dict()
    for vuln_info in vuln_ids_dict.values():
        if not vuln_info["valid"]:
            continue
        for ssvc_priority in vuln_info["ssvc_priority_list"]:
            ticket_counts_dict[ssvc_priority.value] += 1

    return ticket_counts_dict


def _create_initial_ticket_counts_dict() -> dict:
    immediate = models.SSVCDeployerPriorityEnum.IMMEDIATE.value
    out_of_cycle = models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE.value
    scheduled = models.SSVCDeployerPriorityEnum.SCHEDULED.value
    defer = models.SSVCDeployerPriorityEnum.DEFER.value

    return {
        immediate: 0,
        out_of_cycle: 0,
        scheduled: 0,
        defer: 0,
    }

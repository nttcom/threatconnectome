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
    _completed = models.VulnStatusType.completed
    vuln_ids_dict = {}
    dependencies = dependency_business.get_dependencies_by_service(db, service, package_id)

    for dependency in dependencies:
        for ticket in dependency.tickets:
            ssvc_priority = ticket.ssvc_deployer_priority or models.SSVCDeployerPriorityEnum.DEFER

            if related_ticket_status == "solved" and ticket.ticket_status.vuln_status != _completed:
                continue
            elif (
                related_ticket_status == "unsolved"
                and ticket.ticket_status.vuln_status == _completed
            ):
                continue

            if ticket.threat.vuln_id not in vuln_ids_dict:
                vuln_ids_dict[ticket.threat.vuln_id] = {
                    "vuln_id": ticket.threat.vuln_id,
                    "highest_ssvc_priority": ssvc_priority,
                    "vuln_updated_at": ticket.threat.vuln.updated_at,
                }
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
    ticket_counts_dict: dict = _create_initial_ticket_counts_dict()

    _completed = models.VulnStatusType.completed

    dependencies = dependency_business.get_dependencies_by_service(db, service, package_id)
    for dependency in dependencies:
        if package_id and dependency.package_version.package_id != str(package_id):
            continue
        for ticket in dependency.tickets:
            ssvc_priority = ticket.ssvc_deployer_priority or models.SSVCDeployerPriorityEnum.DEFER

            if related_ticket_status == "solved" and ticket.ticket_status.vuln_status != _completed:
                continue
            elif (
                related_ticket_status == "unsolved"
                and ticket.ticket_status.vuln_status == _completed
            ):
                continue

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

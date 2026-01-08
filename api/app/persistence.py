from typing import Sequence
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app import models

### Account


def get_account_by_uid(db: Session, uid: str) -> models.Account | None:
    return db.scalars(select(models.Account).where(models.Account.uid == uid)).one_or_none()


def get_accounts_by_email(db: Session, email: str) -> Sequence[models.Account]:
    return db.scalars(select(models.Account).where(models.Account.email == email)).all()


def get_account_by_id(db: Session, user_id: UUID | str) -> models.Account | None:
    return db.scalars(
        select(models.Account).where(models.Account.user_id == str(user_id))
    ).one_or_none()


def create_account(db: Session, account: models.Account) -> None:
    db.add(account)
    db.flush()


def delete_account(db: Session, account: models.Account) -> None:
    db.delete(account)
    db.flush()


### AccountDefaultPTeam
def get_account_default_pteam_by_user_id(
    db: Session, user_id: UUID | str
) -> models.AccountDefaultPTeam | None:
    return db.scalars(
        select(models.AccountDefaultPTeam).where(
            models.AccountDefaultPTeam.user_id == str(user_id),
        )
    ).one_or_none()


def get_account_default_pteam_by_user_id_and_pteam_id(
    db: Session, user_id: UUID | str, pteam_id: UUID | str
) -> models.AccountDefaultPTeam | None:
    return db.scalars(
        select(models.AccountDefaultPTeam).where(
            models.AccountDefaultPTeam.user_id == str(user_id),
            models.AccountDefaultPTeam.default_pteam_id == str(pteam_id),
        )
    ).one_or_none()


def create_account_default_pteam(
    db: Session, account_default_pteam: models.AccountDefaultPTeam
) -> None:
    db.add(account_default_pteam)
    db.flush()


def delete_account_default_pteam(
    db: Session, account_default_pteam: models.AccountDefaultPTeam
) -> None:
    db.delete(account_default_pteam)
    db.flush()


### ActionLog


def get_action_log_by_id(db: Session, logging_id: UUID | str) -> models.ActionLog | None:
    return db.scalars(
        select(models.ActionLog).where(models.ActionLog.logging_id == str(logging_id))
    ).one_or_none()


def get_action_logs_by_user_id(db: Session, user_id: UUID | str) -> Sequence[models.ActionLog]:
    return db.scalars(
        select(models.ActionLog).where(
            models.ActionLog.pteam_id.in_(
                db.scalars(
                    select(models.PTeamAccountRole.pteam_id).where(
                        models.PTeamAccountRole.user_id == str(user_id)
                    )
                )
            )
        )
    ).all()


def create_action_log(db: Session, action_log: models.ActionLog) -> None:
    db.add(action_log)
    db.flush()


def get_vuln_logs_by_user_id(
    db: Session,
    vuln_id: UUID | str,
    user_id: UUID | str,
) -> Sequence[models.ActionLog]:
    return db.scalars(
        select(models.ActionLog).where(
            models.ActionLog.vuln_id == str(vuln_id),
            models.ActionLog.pteam_id.in_(
                db.scalars(
                    select(models.PTeamAccountRole.pteam_id).where(
                        models.PTeamAccountRole.user_id == str(user_id)
                    )
                )
            ),
        )
    ).all()


### Affect


def create_affect(db: Session, affect: models.Affect) -> None:
    db.add(affect)
    db.flush()


def delete_affect(db: Session, affect: models.Affect) -> None:
    db.delete(affect)
    db.flush()


### AffectedObject


def create_affected_object(db: Session, affected_object: models.AffectedObject):
    db.add(affected_object)
    db.flush()


def delete_affected_object(db: Session, affected_object: models.AffectedObject) -> None:
    db.delete(affected_object)
    db.flush()


### Insight


def create_insight(db: Session, insight: models.Insight):
    db.add(insight)
    db.flush()


def delete_insight(db: Session, insight: models.Insight) -> None:
    db.delete(insight)
    db.flush()


### InsightReference


def create_insight_reference(db: Session, insight_reference: models.InsightReference):
    db.add(insight_reference)
    db.flush()


def delete_insight_reference(db: Session, insight_reference: models.InsightReference) -> None:
    db.delete(insight_reference)
    db.flush()


### ThreatScenarios


def delete_threat_scenario(db: Session, threat_scenario: models.ThreatScenario) -> None:
    db.delete(threat_scenario)
    db.flush()


### PTeam


def get_all_pteams(db: Session) -> Sequence[models.PTeam]:
    return db.scalars(select(models.PTeam)).all()


def get_pteam_by_id(db: Session, pteam_id: UUID | str) -> models.PTeam | None:
    return db.scalars(
        select(models.PTeam).where(models.PTeam.pteam_id == str(pteam_id))
    ).one_or_none()


def create_pteam(db: Session, pteam: models.PTeam) -> None:
    db.add(pteam)
    db.flush()


def delete_pteam(db: Session, pteam: models.PTeam) -> None:
    db.delete(pteam)
    db.flush()


### PTeamInvitation


def get_pteam_invitations(
    db: Session,
    pteam_id: UUID | str,
) -> Sequence[models.PTeamInvitation]:
    return db.scalars(
        select(models.PTeamInvitation).where(models.PTeamInvitation.pteam_id == str(pteam_id))
    ).all()


def get_pteam_invitation_by_id(
    db: Session,
    invitation_id: UUID | str,
) -> models.PTeamInvitation | None:
    return db.scalars(
        select(models.PTeamInvitation).where(
            models.PTeamInvitation.invitation_id == str(invitation_id)
        )
    ).one_or_none()


def create_pteam_invitation(db: Session, invitation: models.PTeamInvitation) -> None:
    db.add(invitation)
    db.flush()


def delete_pteam_invitation(db: Session, invitation: models.PTeamInvitation) -> None:
    db.delete(invitation)
    db.flush()


### PTeamAccountRole


def get_pteam_account_role(
    db: Session, pteam_id: UUID | str, user_id: UUID | str
) -> models.PTeamAccountRole | None:
    return db.scalars(
        select(models.PTeamAccountRole).where(
            models.PTeamAccountRole.pteam_id == str(pteam_id),
            models.PTeamAccountRole.user_id == str(user_id),
        )
    ).one_or_none()


def create_pteam_account_role(db: Session, account_role: models.PTeamAccountRole) -> None:
    db.add(account_role)
    db.flush()


### Package
def get_package_by_id(db: Session, package_id: UUID | str) -> models.Package | None:
    return db.scalars(
        select(models.Package).where(models.Package.package_id == str(package_id))
    ).one_or_none()


def get_package_by_name_and_ecosystem_and_source_name(
    db: Session, name: str, ecosystem: str, source_name: str | None
) -> models.Package | None:
    return db.scalars(
        select(models.Package).where(
            and_(
                models.Package.name == name,
                models.Package.ecosystem == ecosystem,
                models.OSPackage.source_name == source_name,
            )
        )
    ).one_or_none()


def create_package(db: Session, package: models.Package) -> None:
    db.add(package)
    db.flush()


def delete_package(db: Session, package: models.Package) -> None:
    db.delete(package)
    db.flush()


### PackageVersion
def get_package_version_by_id(
    db: Session, package_version_id: UUID | str
) -> models.PackageVersion | None:
    return db.scalars(
        select(models.PackageVersion).where(
            models.PackageVersion.package_version_id == str(package_version_id)
        )
    ).one_or_none()


def get_package_version_by_package_id_and_version(
    db: Session, package_id: UUID | str, version: str
) -> models.PackageVersion | None:
    return db.scalars(
        select(models.PackageVersion).where(
            and_(
                models.PackageVersion.package_id == str(package_id),
                models.PackageVersion.version == version,
            )
        )
    ).one_or_none()


def create_package_version(db: Session, package_version: models.PackageVersion) -> None:
    db.add(package_version)
    db.flush()


def delete_package_version(db: Session, package_version: models.PackageVersion) -> None:
    db.delete(package_version)
    db.flush()


### Threat


def create_threat(db: Session, threat: models.Threat) -> None:
    db.add(threat)
    db.flush()


def delete_threat(db: Session, threat: models.Threat) -> None:
    db.delete(threat)
    db.flush()


def get_threat_by_package_version_id_and_vuln_id(
    db: Session, package_version_id: UUID | str, vuln_id: UUID | str
) -> models.Threat | None:
    return db.scalars(
        select(models.Threat).where(
            models.Threat.package_version_id == str(package_version_id),
            models.Threat.vuln_id == str(vuln_id),
        )
    ).one_or_none()


### ThreatScenario


def create_threat_scenario(db: Session, threat_scenario: models.ThreatScenario):
    db.add(threat_scenario)
    db.flush()


### Ticket


def create_ticket(db: Session, ticket: models.Ticket) -> None:
    db.add(ticket)
    db.flush()


def delete_ticket(db: Session, ticket: models.Ticket) -> None:
    db.delete(ticket)
    db.flush()


def get_ticket_by_id(db: Session, ticket_id: UUID | str) -> models.Ticket | None:
    return db.scalars(
        select(models.Ticket).where(models.Ticket.ticket_id == str(ticket_id))
    ).one_or_none()


def get_ticket_by_threat_id_and_dependency_id(
    db: Session, threat_id: UUID | str, dependency_id: UUID | str
) -> models.Ticket | None:
    return db.scalars(
        select(models.Ticket).where(
            models.Ticket.threat_id == str(threat_id),
            models.Ticket.dependency_id == str(dependency_id),
        )
    ).one_or_none()


def get_pteams_by_ids(db: Session, pteam_ids: list[UUID]):
    str_pteam_ids = [str(pid) for pid in pteam_ids]
    return db.query(models.PTeam).filter(models.PTeam.pteam_id.in_(str_pteam_ids)).all()


### TicketStatus


def create_ticket_status(
    db: Session,
    status: models.TicketStatus,
) -> None:
    db.add(status)
    db.flush()


### Vuln
def get_vuln_by_id(db: Session, vuln_id: UUID | str) -> models.Vuln | None:
    return db.scalars(select(models.Vuln).where(models.Vuln.vuln_id == str(vuln_id))).one_or_none()


def create_vuln(db: Session, vuln: models.Vuln):
    db.add(vuln)
    db.flush()


def delete_vuln(db: Session, vuln: models.Vuln) -> None:
    db.delete(vuln)
    db.flush()


### Service


def get_service_by_id(db: Session, service_id: UUID | str) -> models.Service | None:
    return db.scalars(
        select(models.Service).where(models.Service.service_id == str(service_id))
    ).one_or_none()


### Dependency


def get_dependency_by_id(db: Session, dependency_id: UUID | str) -> models.Dependency | None:
    return db.scalars(
        select(models.Dependency).where(models.Dependency.dependency_id == str(dependency_id))
    ).one_or_none()


def get_dependencies_from_service_id_and_package_id(
    db: Session, service_id: UUID | str, package_id: UUID | str
) -> Sequence[models.Dependency]:
    return db.scalars(
        select(models.Dependency)
        .join(models.PackageVersion)
        .where(
            models.Dependency.service_id == str(service_id),
            models.PackageVersion.package_id == str(package_id),
        )
    ).all()


### Alert


def create_alert(db: Session, alert: models.Alert) -> None:
    db.add(alert)
    db.flush()


### EolProduct
def get_eol_product_by_id(db: Session, eol_product_id: UUID | str) -> models.EoLProduct | None:
    return db.scalars(
        select(models.EoLProduct).where(models.EoLProduct.eol_product_id == str(eol_product_id))
    ).one_or_none()


def create_eol_product(db: Session, eol: models.EoLProduct):
    db.add(eol)
    db.flush()


def delete_eol_product(db: Session, eol: models.EoLProduct) -> None:
    db.delete(eol)
    db.flush()


### EolVersion
def create_eol_version(db: Session, eol: models.EoLVersion):
    db.add(eol)
    db.flush()


def delete_eol_version(db: Session, eol: models.EoLVersion) -> None:
    db.delete(eol)
    db.flush()

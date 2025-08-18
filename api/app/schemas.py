import re
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants import DEFAULT_ALERT_SSVC_PRIORITY
from app.models import (
    ActionType,
    AutomatableEnum,
    ExploitationEnum,
    ImpactCategoryEnum,
    MissionImpactEnum,
    SafetyImpactEnum,
    SSVCDeployerPriorityEnum,
    SystemExposureEnum,
    VulnStatusType,
)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class VulnSortKey(str, Enum):
    CVSS_V3_SCORE = "cvss_v3_score"
    CVSS_V3_SCORE_DESC = "cvss_v3_score_desc"
    UPDATED_AT = "updated_at"
    UPDATED_AT_DESC = "updated_at_desc"


class RelatedTicketStatus(str, Enum):
    SOLVED = "solved"
    UNSOLVED = "unsolved"


class Token(ORMModel):
    access_token: str
    token_type: str
    refresh_token: str


class RefreshTokenRequest(ORMModel):
    refresh_token: str


class Mail(ORMModel):
    enable: bool
    address: str


class Slack(ORMModel):
    enable: bool
    webhook_url: str


class PTeamEntry(ORMModel):
    pteam_id: UUID
    pteam_name: str
    contact_info: str


class PTeamRole(ORMModel):
    is_admin: bool
    pteam: PTeamEntry


class UserResponse(ORMModel):
    user_id: UUID
    uid: str
    email: str
    disabled: bool
    years: int
    pteam_roles: list[PTeamRole]


class PteamMemberGetResponse(ORMModel):
    user_id: UUID
    uid: str
    email: str
    disabled: bool
    years: int
    is_admin: bool


class UserCreateRequest(ORMModel):
    years: int = 0


class UserUpdateRequest(ORMModel):
    disabled: bool | None = None
    years: int | None = None


class ActionResponse(ORMModel):
    vuln_id: UUID
    action_id: UUID
    action: str = Field(..., max_length=1024)
    action_type: ActionType
    recommended: bool
    created_at: datetime


class PackageFileResponse(ORMModel):
    class Reference(ORMModel):
        service: str
        target: str
        package_manager: str
        version: str

    package_id: UUID
    package_name: str
    ecosystem: str
    references: list[Reference] = []


class PTeamServiceResponse(ORMModel):
    service_name: str
    service_id: UUID
    sbom_uploaded_at: datetime | None = None
    description: str | None
    keywords: list[str]
    system_exposure: SystemExposureEnum
    service_mission_impact: MissionImpactEnum
    service_safety_impact: SafetyImpactEnum


class PTeamServiceUpdateRequest(ORMModel):
    service_name: str | None = None
    description: str | None = None
    keywords: list[str] | None = None
    system_exposure: SystemExposureEnum | None = None
    service_mission_impact: MissionImpactEnum | None = None
    service_safety_impact: SafetyImpactEnum | None = None


class PTeamServiceUpdateResponse(ORMModel):
    service_name: str
    description: str | None
    keywords: list[str]
    system_exposure: SystemExposureEnum | None
    service_mission_impact: MissionImpactEnum | None
    service_safety_impact: SafetyImpactEnum | None


CVE_PATTERN = r"^CVE-\d{4}-\d{4,}$"


def validate_cve_id(value):
    if value is None:
        return value
    if not re.match(CVE_PATTERN, value):
        raise ValueError(f"Invalid CVE ID format: {value}")
    return value


class ActionCreateRequest(ORMModel):
    vuln_id: UUID
    action: str = Field(..., max_length=1024)
    action_type: ActionType
    recommended: bool = False


class ActionUpdateRequest(ORMModel):
    action: str | None = None
    action_type: ActionType | None = None
    recommended: bool | None = None


class VulnerablePackageResponse(BaseModel):
    affected_name: str
    ecosystem: str
    affected_versions: list[str]
    fixed_versions: list[str]


class VulnBase(BaseModel):
    title: str | None = None
    cve_id: str | None = None
    detail: str | None = None
    exploitation: ExploitationEnum | None = None
    automatable: AutomatableEnum | None = None
    cvss_v3_score: float | None = None
    vulnerable_packages: list[VulnerablePackageResponse] = []

    _validate_cve_id = field_validator("cve_id", mode="before")(validate_cve_id)


class VulnResponse(VulnBase):
    vuln_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None


class VulnsListResponse(BaseModel):
    num_vulns: int
    vulns: list[VulnResponse]


class VulnUpdateRequest(VulnBase):
    pass


class ThreatScenario(BaseModel):
    impact_category: ImpactCategoryEnum
    title: str
    description: str


class AffectedObject(BaseModel):
    object_category: str
    name: str
    description: str


class InsightReference(BaseModel):
    link_text: str
    url: str


class InsightBase(BaseModel):
    description: str
    reasoning_and_planing: str
    threat_scenarios: list[ThreatScenario] = []
    affected_objects: list[AffectedObject] = []
    insight_references: list[InsightReference] = []


class InsightRequest(InsightBase):
    pass


class InsightResponse(InsightBase):
    insight_id: UUID
    ticket_id: UUID
    created_at: datetime
    updated_at: datetime


class InsighUpdatetRequest(BaseModel):
    description: str | None = None
    reasoning_and_planing: str | None = None
    threat_scenarios: list[ThreatScenario] | None = None
    affected_objects: list[AffectedObject] | None = None
    insight_references: list[InsightReference] | None = None


class PTeamInfo(PTeamEntry):
    alert_slack: Slack
    alert_ssvc_priority: SSVCDeployerPriorityEnum
    services: list[PTeamServiceResponse]
    alert_mail: Mail


class PTeamCreateRequest(ORMModel):
    pteam_name: str
    contact_info: str = ""
    alert_slack: Slack | None = None
    alert_ssvc_priority: SSVCDeployerPriorityEnum = SSVCDeployerPriorityEnum(
        DEFAULT_ALERT_SSVC_PRIORITY
    )
    alert_mail: Mail | None = None


class PTeamUpdateRequest(ORMModel):
    pteam_name: str | None = None
    contact_info: str | None = None
    alert_slack: Slack | None = None
    alert_ssvc_priority: SSVCDeployerPriorityEnum | None = None
    alert_mail: Mail | None = None


class PTeamAuthInfo(ORMModel):
    class PTeamAuthEntry(ORMModel):
        enum: str
        name: str
        desc: str

    class PseudoUUID(ORMModel):
        name: str
        uuid: UUID

    authorities: list[PTeamAuthEntry]
    pseudo_uuids: list[PseudoUUID]


class PTeamMemberUpdateRequest(ORMModel):
    is_admin: bool


class PTeamMemberUpdateResponse(ORMModel):
    pteam_id: UUID
    user_id: UUID
    is_admin: bool


class PTeamInvitationRequest(ORMModel):
    expiration: datetime
    limit_count: int | None = None


class PTeamInvitationResponse(ORMModel):
    invitation_id: UUID
    pteam_id: UUID
    expiration: datetime
    limit_count: int | None = None  # None for unlimited
    used_count: int


class PTeamInviterResponse(ORMModel):
    pteam_id: UUID
    pteam_name: str
    email: str
    user_id: UUID


class ApplyInvitationRequest(ORMModel):
    invitation_id: UUID


class ActionLogResponse(ORMModel):
    logging_id: UUID
    action_id: UUID | None = None
    vuln_id: UUID
    action: str
    action_type: ActionType
    recommended: bool
    user_id: UUID | None = None
    pteam_id: UUID
    service_id: UUID
    ticket_id: UUID
    email: str
    executed_at: datetime
    created_at: datetime


class ActionLogRequest(ORMModel):
    action_id: UUID | None = None
    action: str
    action_type: ActionType
    recommended: bool
    vuln_id: UUID
    user_id: UUID
    pteam_id: UUID
    service_id: UUID
    ticket_id: UUID
    executed_at: datetime | None = None


class TicketStatusRequest(ORMModel):
    vuln_status: VulnStatusType | None = None
    logging_ids: list[UUID] | None = None
    assignees: list[UUID] | None = None
    note: str | None = None
    scheduled_at: datetime | None = None


class TicketStatusResponse(ORMModel):
    status_id: UUID
    ticket_id: UUID
    vuln_status: VulnStatusType
    user_id: UUID | None  # None: auto created when ticket is created
    created_at: datetime
    assignees: list[UUID] = []
    note: str | None = None
    scheduled_at: datetime | None = None
    action_logs: list[ActionLogResponse] = []


class TicketResponse(ORMModel):
    ticket_id: UUID
    vuln_id: UUID
    dependency_id: UUID
    service_id: UUID
    pteam_id: UUID
    created_at: datetime
    ssvc_deployer_priority: SSVCDeployerPriorityEnum | None
    ticket_safety_impact: SafetyImpactEnum | None
    ticket_safety_impact_change_reason: str | None
    ticket_status: TicketStatusResponse


class TicketListResponse(BaseModel):
    total: int
    tickets: list[TicketResponse]


class TicketUpdateRequest(ORMModel):
    ticket_safety_impact: SafetyImpactEnum | None = None
    ticket_safety_impact_change_reason: str | None = None


class PTeamPackagesSummary(ORMModel):
    class PTeamPackageSummary(ORMModel):
        package_id: UUID
        package_name: str
        ecosystem: str
        package_managers: list[str]
        service_ids: list[UUID]
        ssvc_priority: SSVCDeployerPriorityEnum | None
        updated_at: datetime | None
        status_count: dict[str, int]  # VUlnStatusType.value: tickets count

    ssvc_priority_count: dict[SSVCDeployerPriorityEnum, int]  # priority: packages count
    packages: list[PTeamPackageSummary]


class SlackCheckRequest(ORMModel):
    slack_webhook_url: str


class EmailCheckRequest(ORMModel):
    email: str


class ServicePackageVulnsSolvedUnsolved(ORMModel):
    pteam_id: UUID
    service_id: UUID | None
    package_id: UUID | None
    related_ticket_status: RelatedTicketStatus | None
    vuln_ids: list[UUID]


class ServicePackageTicketCountsSolvedUnsolved(ORMModel):
    pteam_id: UUID
    service_id: UUID | None
    package_id: UUID | None
    related_ticket_status: RelatedTicketStatus | None
    ssvc_priority_count: dict[str, int]


class DependencyResponse(ORMModel):
    dependency_id: UUID
    service_id: UUID
    package_version_id: UUID
    package_id: UUID
    package_manager: str
    target: str
    dependency_mission_impact: str | None = None
    package_name: str
    package_source_name: str | None = None
    package_version: str
    package_ecosystem: str
    vuln_matching_ecosystem: str

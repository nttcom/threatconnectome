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
    MissionImpactEnum,
    SafetyImpactEnum,
    SSVCDeployerPriorityEnum,
    SystemExposureEnum,
    TopicStatusType,
)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TopicSortKey(str, Enum):
    CVSS_V3_SCORE = "cvss_v3_score"
    CVSS_V3_SCORE_DESC = "cvss_v3_score_desc"
    UPDATED_AT = "updated_at"
    UPDATED_AT_DESC = "updated_at_desc"


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


class UserCreateRequest(ORMModel):
    years: int = 0


class UserUpdateRequest(ORMModel):
    disabled: bool | None = None
    years: int | None = None


class ActionResponse(ORMModel):
    topic_id: UUID
    action_id: UUID
    action: str = Field(..., max_length=1024)
    action_type: ActionType
    recommended: bool
    created_by: UUID
    created_at: datetime
    ext: dict  # see ActionCreateRequest


class TagRequest(ORMModel):
    tag_name: str


class TagResponse(ORMModel):
    tag_id: UUID
    tag_name: str
    parent_id: UUID | None = None
    parent_name: str | None = None


class ExtTagResponse(TagResponse):
    references: list[dict] = []


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
    description: str | None = None
    keywords: list[str] | None = None
    system_exposure: SystemExposureEnum | None = None
    service_mission_impact: MissionImpactEnum | None = None
    service_safety_impact: SafetyImpactEnum | None = None


class PTeamServiceUpdateResponse(ORMModel):
    description: str | None
    keywords: list[str]
    system_exposure: SystemExposureEnum | None
    service_mission_impact: MissionImpactEnum | None
    service_safety_impact: SafetyImpactEnum | None


class MispTagRequest(ORMModel):
    tag_name: str


class MispTagResponse(ORMModel):
    tag_id: UUID
    tag_name: str


CVE_PATTERN = r"^CVE-\d{4}-\d{4,}$"


def validate_cve_id(value):
    if value is None:
        return value
    if not re.match(CVE_PATTERN, value):
        raise ValueError(f"Invalid CVE ID format: {value}")
    return value


class TopicEntry(ORMModel):
    topic_id: UUID
    title: str
    content_fingerprint: str
    updated_at: datetime


class Topic(TopicEntry):
    topic_id: UUID
    title: str
    abstract: str
    created_by: UUID
    created_at: datetime
    exploitation: ExploitationEnum | None
    automatable: AutomatableEnum | None
    cvss_v3_score: float | None
    cve_id: str | None

    _validate_cve_id = field_validator("cve_id", mode="before")(validate_cve_id)


class TopicResponse(Topic):
    tags: list[TagResponse]
    misp_tags: list[MispTagResponse]


class TopicCreateResponse(TopicResponse):
    actions: list[ActionResponse]


class SearchTopicsResponse(ORMModel):
    num_topics: int
    offset: int | None = None
    limit: int | None = None
    sort_key: TopicSortKey
    topics: list[TopicEntry]


class TopicActionsResponse(ORMModel):
    topic_id: UUID
    pteam_id: UUID
    actions: list[ActionResponse]


class ActionCreateRequest(ORMModel):
    topic_id: UUID | None = None  # can be None if using in create_topic()
    action_id: UUID | None = None  # can specify action_id by client
    action: str = Field(..., max_length=1024)
    action_type: ActionType
    recommended: bool = False
    ext: dict = {}
    # {
    #   tags: list[str] = [],
    #   vulnerable_versions: Dict[str, list[dict]] = {},  # see around auto-close for detail.
    # }


class ActionUpdateRequest(ORMModel):
    action: str | None = None
    action_type: ActionType | None = None
    recommended: bool | None = None
    ext: dict | None = None


class TopicCreateRequest(ORMModel):
    title: str
    abstract: str
    tags: list[str] = []
    misp_tags: list[str] = []
    actions: list[ActionCreateRequest] = []
    exploitation: ExploitationEnum | None = None
    automatable: AutomatableEnum | None = None
    cvss_v3_score: float | None = None
    cve_id: str | None = None

    _validate_cve_id = field_validator("cve_id", mode="before")(validate_cve_id)


class TopicUpdateRequest(ORMModel):
    title: str | None = None
    abstract: str | None = None
    tags: list[str] | None = None
    misp_tags: list[str] | None = None
    exploitation: ExploitationEnum | None = None
    automatable: AutomatableEnum | None = None
    cvss_v3_score: float | None = None
    cve_id: str | None = None

    _validate_cve_id = field_validator("cve_id", mode="before")(validate_cve_id)


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


class PTeamMemberRequest(ORMModel):
    is_admin: bool


class PTeamMemberResponse(ORMModel):
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
    action_id: UUID
    topic_id: UUID
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
    action_id: UUID
    topic_id: UUID
    user_id: UUID
    pteam_id: UUID
    service_id: UUID
    ticket_id: UUID
    executed_at: datetime | None = None


class ThreatResponse(ORMModel):
    threat_id: UUID
    dependency_id: UUID
    topic_id: UUID
    threat_safety_impact: SafetyImpactEnum | None = None


class ThreatUpdateRequest(ORMModel):
    threat_safety_impact: SafetyImpactEnum | None = None


class TicketStatusRequest(ORMModel):
    topic_status: TopicStatusType | None = None
    logging_ids: list[UUID] | None = None
    assignees: list[UUID] | None = None
    note: str | None = None
    scheduled_at: datetime | None = None


class TicketStatusResponse(ORMModel):
    status_id: UUID
    ticket_id: UUID
    topic_status: TopicStatusType
    user_id: UUID | None  # None: auto created when ticket is created
    created_at: datetime
    assignees: list[UUID] = []
    note: str | None = None
    scheduled_at: datetime | None = None
    action_logs: list[ActionLogResponse] = []


class TicketResponse(ORMModel):
    ticket_id: UUID
    threat_id: UUID
    created_at: datetime
    ssvc_deployer_priority: SSVCDeployerPriorityEnum | None
    threat: ThreatResponse
    ticket_status: TicketStatusResponse


class PTeamTagSummary(ORMModel):
    tag_id: UUID
    tag_name: str
    parent_id: UUID | None
    parent_name: str | None
    service_ids: list[UUID]
    ssvc_priority: SSVCDeployerPriorityEnum | None
    updated_at: datetime | None
    status_count: dict[str, int]


class PTeamTagsSummary(ORMModel):
    ssvc_priority_count: dict[SSVCDeployerPriorityEnum, int]  # ssvc_priority: tags count
    tags: list[PTeamTagSummary]


class PTeamServiceTagsSummary(ORMModel):
    class PTeamServiceTagSummary(ORMModel):
        tag_id: UUID
        tag_name: str
        parent_id: UUID | None
        parent_name: str | None
        ssvc_priority: SSVCDeployerPriorityEnum | None
        updated_at: datetime | None
        status_count: dict[str, int]  # TopicStatusType.value: tickets count

    ssvc_priority_count: dict[SSVCDeployerPriorityEnum, int]  # priority: tags count
    tags: list[PTeamServiceTagSummary]


class SlackCheckRequest(ORMModel):
    slack_webhook_url: str


class EmailCheckRequest(ORMModel):
    email: str


class ServiceTaggedTopics(ORMModel):
    ssvc_priority_count: dict[str, int]
    topic_ids: list[UUID]


class ServiceTaggedTopicsSolvedUnsolved(ORMModel):
    pteam_id: UUID
    service_id: UUID
    tag_id: UUID
    solved: ServiceTaggedTopics
    unsolved: ServiceTaggedTopics


class DependencyResponse(ORMModel):
    dependency_id: UUID
    service_id: UUID
    tag_id: UUID
    version: str
    target: str

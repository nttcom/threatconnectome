from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants import DEFAULT_ALERT_SSVC_PRIORITY
from app.models import (
    ActionType,
    ATeamAuthEnum,
    AutomatableEnum,
    ExploitationEnum,
    MissionImpactEnum,
    PTeamAuthEnum,
    SafetyImpactEnum,
    SSVCDeployerPriorityEnum,
    SystemExposureEnum,
    TopicStatusType,
)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TopicSortKey(str, Enum):
    THREAT_IMPACT = "threat_impact"
    THREAT_IMPACT_DESC = "threat_impact_desc"
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


class User(ORMModel):
    user_id: UUID
    email: str


class PTeamEntry(ORMModel):
    pteam_id: UUID
    pteam_name: str
    contact_info: str


class ATeamEntry(ORMModel):
    ateam_id: UUID
    ateam_name: str
    contact_info: str


class UserResponse(ORMModel):
    user_id: UUID
    uid: str
    email: str
    disabled: bool
    years: int
    pteams: list[PTeamEntry]
    ateams: list[ATeamEntry]


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


class ExtTagRequest(TagRequest):
    references: list[dict] | None = []


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
    safety_impact: SafetyImpactEnum


class PTeamServiceUpdateRequest(ORMModel):
    description: str | None = None
    keywords: list[str] | None = None
    system_exposure: SystemExposureEnum | None = None
    service_mission_impact: MissionImpactEnum | None = None
    safety_impact: SafetyImpactEnum | None = None


class PTeamServiceUpdateResponse(ORMModel):
    description: str | None
    keywords: list[str]
    system_exposure: SystemExposureEnum | None
    service_mission_impact: MissionImpactEnum | None
    safety_impact: SafetyImpactEnum | None


class PTeamtagRequest(ORMModel):
    references: list[dict] | None = None


class PTeamtagResponse(ORMModel):
    pteam_id: UUID
    tag_id: UUID
    references: list[dict]


class PTeamtagExtResponse(PTeamtagResponse):
    last_updated_at: datetime | None = None


class MispTagRequest(ORMModel):
    tag_name: str


class MispTagResponse(ORMModel):
    tag_id: UUID
    tag_name: str


def threat_impact_range(value):
    assert value is None or 0 < value <= 4, "Specify a threat_impact between 1 and 4"
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
    threat_impact: int
    created_by: UUID
    created_at: datetime
    exploitation: ExploitationEnum | None
    automatable: AutomatableEnum | None

    _threat_impact_range = field_validator("threat_impact", mode="before")(threat_impact_range)


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
    threat_impact: int
    tags: list[str] = []
    misp_tags: list[str] = []
    actions: list[ActionCreateRequest] = []
    exploitation: ExploitationEnum | None = None
    automatable: AutomatableEnum | None = None

    _threat_impact_range = field_validator("threat_impact", mode="before")(threat_impact_range)


class TopicUpdateRequest(ORMModel):
    title: str | None = None
    abstract: str | None = None
    threat_impact: int | None = None
    tags: list[str] | None = None
    misp_tags: list[str] | None = None
    exploitation: ExploitationEnum | None = None
    automatable: AutomatableEnum | None = None

    _threat_impact_range = field_validator("threat_impact", mode="before")(threat_impact_range)


class PTeamInfo(PTeamEntry):
    alert_slack: Slack
    alert_ssvc_priority: SSVCDeployerPriorityEnum
    services: list[PTeamServiceResponse]
    ateams: list[ATeamEntry]
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


class PTeamAuthRequest(ORMModel):
    user_id: UUID
    authorities: list[PTeamAuthEnum]


class PTeamAuthResponse(ORMModel):
    user_id: UUID
    authorities: list[PTeamAuthEnum]


class PTeamInvitationRequest(ORMModel):
    expiration: datetime
    limit_count: int | None = None
    authorities: list[PTeamAuthEnum] | None = None  # require ADMIN for not-None


class PTeamInvitationResponse(ORMModel):
    invitation_id: UUID
    pteam_id: UUID
    expiration: datetime
    limit_count: int | None = None  # None for unlimited
    used_count: int
    authorities: list[PTeamAuthEnum]


class PTeamInviterResponse(ORMModel):
    pteam_id: UUID
    pteam_name: str
    email: str
    user_id: UUID


class ATeamInfo(ATeamEntry):
    alert_slack: Slack
    alert_mail: Mail
    pteams: list[PTeamInfo]


class ApplyInvitationRequest(ORMModel):  # common use of PTeam and ATeam
    invitation_id: UUID


class ATeamCreateRequest(ORMModel):
    ateam_name: str
    contact_info: str = ""
    alert_slack: Slack | None = None
    alert_mail: Mail | None = None


class ATeamUpdateRequest(ORMModel):
    ateam_name: str | None = None
    contact_info: str | None = None
    alert_slack: Slack | None = None
    alert_mail: Mail | None = None


class ATeamAuthInfo(ORMModel):
    class ATeamAuthEntry(ORMModel):
        enum: str
        name: str
        desc: str

    class PseudoUUID(ORMModel):
        name: str
        uuid: UUID

    authorities: list[ATeamAuthEntry]
    pseudo_uuids: list[PseudoUUID]


class ATeamAuthRequest(ORMModel):
    user_id: UUID
    authorities: list[ATeamAuthEnum]


class ATeamAuthResponse(ORMModel):
    user_id: UUID
    authorities: list[ATeamAuthEnum]


class ATeamInvitationRequest(ORMModel):
    expiration: datetime
    limit_count: int | None = None  # None for unlimited
    authorities: list[ATeamAuthEnum] | None = None  # require ADMIN for not-None


class ATeamInvitationResponse(ORMModel):
    invitation_id: UUID
    ateam_id: UUID
    expiration: datetime
    limit_count: int | None = None
    used_count: int
    authorities: list[ATeamAuthEnum]


class ATeamInviterResponse(ORMModel):
    ateam_id: UUID
    ateam_name: str
    email: str
    user_id: UUID


class ATeamWatchingRequestRequest(ORMModel):
    expiration: datetime
    limit_count: int | None = None  # None for unlimited


class ATeamWatchingRequestResponse(ORMModel):
    request_id: UUID
    ateam_id: UUID
    expiration: datetime
    limit_count: int | None = None
    used_count: int


class ATeamRequesterResponse(ORMModel):
    ateam_id: UUID
    ateam_name: str
    email: str
    user_id: UUID


class ApplyWatchingRequestRequest(ORMModel):
    request_id: UUID
    pteam_id: UUID


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


class TopicStatusRequest(ORMModel):
    topic_status: TopicStatusType
    logging_ids: list[UUID] = []
    assignees: list[UUID] = []
    note: str | None = None
    scheduled_at: datetime | None = None


class TopicStatusResponse(ORMModel):
    status_id: UUID | None = None  # None is the case no status is set yet
    topic_id: UUID
    pteam_id: UUID
    service_id: UUID
    tag_id: UUID
    user_id: UUID | None = None
    topic_status: TopicStatusType | None = None
    created_at: datetime | None = None
    assignees: list[UUID] = []
    note: str | None = None
    scheduled_at: datetime | None = None
    action_logs: list[ActionLogResponse] = []


class ThreatResponse(ORMModel):
    threat_id: UUID
    dependency_id: UUID
    topic_id: UUID


class ThreatRequest(ORMModel):
    dependency_id: UUID
    topic_id: UUID


class TicketStatusRequest(ORMModel):
    topic_status: TopicStatusType | None = None
    logging_ids: list[UUID] | None = None
    assignees: list[UUID] | None = None
    note: str | None = None
    scheduled_at: datetime | None = None


class TicketStatusResponse(ORMModel):
    status_id: UUID | None = None  # None is the case no status is set yet
    ticket_id: UUID
    topic_status: TopicStatusType = TopicStatusType.alerted
    user_id: UUID | None = None
    created_at: datetime | None = None
    assignees: list[UUID] = []
    note: str | None = None
    scheduled_at: datetime | None = None
    action_logs: list[ActionLogResponse] = []


class TicketResponse(ORMModel):
    ticket_id: UUID
    threat_id: UUID
    created_at: datetime
    ssvc_deployer_priority: SSVCDeployerPriorityEnum
    threat: ThreatResponse
    current_ticket_status: TicketStatusResponse


class PTeamTaggedTopics(ORMModel):
    pteam_id: UUID
    tag_id: UUID
    threat_impact_count: dict[str, int]
    topic_ids: list[UUID]


class PTeamTopicStatusSummary(ORMModel):
    topic_id: UUID
    threat_impact: int
    updated_at: datetime
    topic_status: TopicStatusType
    executed_at: datetime | None = None


class PTeamTopicStatusesSummary(ORMModel):
    tag_id: UUID
    topics: list[PTeamTopicStatusSummary]


class FsAction(ORMModel):
    action_id: UUID
    topic_id: UUID
    action_type: ActionType
    action: str
    recommended: bool


class FsTopicSummary(ORMModel):
    abstract: str
    actions: list[FsAction]


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
    ssvc_priority_count: dict[str, int]  # ssvc_priority: tags count
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


class FsServerInfo(ORMModel):
    api_url: str


class ServiceTopicStatus(ORMModel):
    service_id: UUID
    service_name: str
    tag: TagResponse
    topic_status: TopicStatusType
    assignees: list[UUID] = []
    scheduled_at: datetime | None = None


class PTeamTopicStatus(ORMModel):
    pteam_id: UUID
    pteam_name: str
    service_statuses: list[ServiceTopicStatus]


class ATeamTopicStatus(ORMModel):
    topic_id: UUID
    title: str
    threat_impact: int
    updated_at: datetime
    num_pteams: int
    pteam_statuses: list[PTeamTopicStatus]


class ATeamTopicStatusResponse(ORMModel):
    num_topics: int
    offset: int | None = None
    limit: int | None = None
    search: str | None = None
    sort_key: str
    topic_statuses: list[ATeamTopicStatus]


class ATeamTopicCommentRequest(ORMModel):
    comment: str


class ATeamTopicCommentResponse(ORMModel):
    comment_id: UUID
    topic_id: UUID
    ateam_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    comment: str
    email: str


class ServiceTaggedTopics(ORMModel):
    threat_impact_count: dict[str, int]
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


class UploadSBOMAcceptedResponse(ORMModel):
    pteam_id: UUID
    service_name: str
    sbom_file_sha256: str

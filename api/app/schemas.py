from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants import DEFAULT_ALERT_THREAT_IMPACT
from app.models import (
    ActionType,
    ATeamAuthEnum,
    PTeamAuthEnum,
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
    disabled: bool


class ATeamEntry(ORMModel):
    ateam_id: UUID
    ateam_name: str
    contact_info: str


class ATeamInfo(ATeamEntry):
    alert_slack: Slack
    alert_mail: Mail
    pteams: List[PTeamEntry]


class UserResponse(ORMModel):
    user_id: UUID
    uid: str
    email: str
    disabled: bool
    years: int
    pteams: List[PTeamEntry]
    ateams: List[ATeamEntry]


class UserCreateRequest(ORMModel):
    years: int = 0


class UserUpdateRequest(ORMModel):
    disabled: Optional[bool] = None
    years: Optional[int] = None


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
    references: Optional[List[dict]] = []


class TagResponse(ORMModel):
    tag_id: UUID
    tag_name: str
    parent_id: Optional[UUID] = None
    parent_name: Optional[str] = None


class ExtTagResponse(TagResponse):
    references: List[dict] = []


class PTeamGroupResponse(ORMModel):
    groups: List[str] = []


class PTeamtagRequest(ORMModel):
    references: Optional[List[dict]] = None


class PTeamtagResponse(ORMModel):
    pteam_id: UUID
    tag_id: UUID
    references: List[dict]


class PTeamtagExtResponse(PTeamtagResponse):
    last_updated_at: Optional[datetime] = None


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
    disabled: bool

    _threat_impact_range = field_validator("threat_impact", mode="before")(threat_impact_range)


class TopicResponse(Topic):
    tags: List[TagResponse]
    misp_tags: List[MispTagResponse]


class TopicCreateResponse(TopicResponse):
    actions: List[ActionResponse]


class SearchTopicsResponse(ORMModel):
    num_topics: int
    offset: Optional[int] = None
    limit: Optional[int] = None
    sort_key: TopicSortKey
    topics: List[TopicEntry]


class TopicActionsResponse(ORMModel):
    topic_id: UUID
    pteam_id: UUID
    actions: List[ActionResponse]


class ActionCreateRequest(ORMModel):
    topic_id: Optional[UUID] = None  # can be None if using in create_topic()
    action_id: Optional[UUID] = None  # can specify action_id by client
    action: str = Field(..., max_length=1024)
    action_type: ActionType
    recommended: bool = False
    ext: dict = {}
    # {
    #   tags: List[str] = [],
    #   vulnerable_versions: Dict[str, List[dict]] = {},  # see around auto-close for detail.
    # }


class ActionUpdateRequest(ORMModel):
    action: Optional[str] = None
    action_type: Optional[ActionType] = None
    recommended: Optional[bool] = None
    ext: Optional[dict] = None


class TopicCreateRequest(ORMModel):
    title: str
    abstract: str
    threat_impact: int
    tags: List[str] = []
    misp_tags: List[str] = []
    actions: List[ActionCreateRequest] = []

    _threat_impact_range = field_validator("threat_impact", mode="before")(threat_impact_range)


class TopicUpdateRequest(ORMModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    threat_impact: Optional[int] = None
    tags: Optional[List[str]] = None
    misp_tags: Optional[List[str]] = None
    disabled: Optional[bool] = None

    _threat_impact_range = field_validator("threat_impact", mode="before")(threat_impact_range)


class PTeamInfo(PTeamEntry):
    alert_slack: Slack
    alert_threat_impact: int
    ateams: List[ATeamEntry]
    alert_mail: Mail

    _threat_impact_range = field_validator("alert_threat_impact", mode="before")(
        threat_impact_range
    )


class PTeamCreateRequest(ORMModel):
    pteam_name: str
    contact_info: str = ""
    alert_slack: Optional[Slack] = None
    alert_threat_impact: int = DEFAULT_ALERT_THREAT_IMPACT
    alert_mail: Optional[Mail] = None

    _threat_impact_range = field_validator("alert_threat_impact", mode="before")(
        threat_impact_range
    )


class PTeamUpdateRequest(ORMModel):
    pteam_name: Optional[str] = None
    contact_info: Optional[str] = None
    alert_slack: Optional[Slack] = None
    alert_threat_impact: Optional[int] = None
    disabled: Optional[bool] = None
    alert_mail: Optional[Mail] = None

    _threat_impact_range = field_validator("alert_threat_impact", mode="before")(
        threat_impact_range
    )


class PTeamAuthInfo(ORMModel):
    class PTeamAuthEntry(ORMModel):
        enum: str
        name: str
        desc: str

    class PseudoUUID(ORMModel):
        name: str
        uuid: UUID

    authorities: List[PTeamAuthEntry]
    pseudo_uuids: List[PseudoUUID]


class PTeamAuthRequest(ORMModel):
    user_id: UUID
    authorities: List[PTeamAuthEnum]


class PTeamAuthResponse(ORMModel):
    user_id: UUID
    authorities: List[PTeamAuthEnum]


class PTeamInvitationRequest(ORMModel):
    expiration: datetime
    limit_count: Optional[int] = None
    authorities: Optional[List[PTeamAuthEnum]] = None  # require ADMIN for not-None


class PTeamInvitationResponse(ORMModel):
    invitation_id: UUID
    pteam_id: UUID
    expiration: datetime
    limit_count: Optional[int] = None  # None for unlimited
    used_count: int
    authorities: List[PTeamAuthEnum]


class PTeamInviterResponse(ORMModel):
    pteam_id: UUID
    pteam_name: str
    email: str
    user_id: UUID


class ApplyInvitationRequest(ORMModel):  # common use of PTeam and ATeam
    invitation_id: UUID


class ATeamCreateRequest(ORMModel):
    ateam_name: str
    contact_info: str = ""
    alert_slack: Optional[Slack] = None
    alert_mail: Optional[Mail] = None


class ATeamUpdateRequest(ORMModel):
    ateam_name: Optional[str] = None
    contact_info: Optional[str] = None
    alert_slack: Optional[Slack] = None
    alert_mail: Optional[Mail] = None


class ATeamAuthInfo(ORMModel):
    class ATeamAuthEntry(ORMModel):
        enum: str
        name: str
        desc: str

    class PseudoUUID(ORMModel):
        name: str
        uuid: UUID

    authorities: List[ATeamAuthEntry]
    pseudo_uuids: List[PseudoUUID]


class ATeamAuthRequest(ORMModel):
    user_id: UUID
    authorities: List[ATeamAuthEnum]


class ATeamAuthResponse(ORMModel):
    user_id: UUID
    authorities: List[ATeamAuthEnum]


class ATeamInvitationRequest(ORMModel):
    expiration: datetime
    limit_count: Optional[int] = None  # None for unlimited
    authorities: Optional[List[ATeamAuthEnum]] = None  # require ADMIN for not-None


class ATeamInvitationResponse(ORMModel):
    invitation_id: UUID
    ateam_id: UUID
    expiration: datetime
    limit_count: Optional[int] = None
    used_count: int
    authorities: List[ATeamAuthEnum]


class ATeamInviterResponse(ORMModel):
    ateam_id: UUID
    ateam_name: str
    email: str
    user_id: UUID


class ATeamWatchingRequestRequest(ORMModel):
    expiration: datetime
    limit_count: Optional[int] = None  # None for unlimited


class ATeamWatchingRequestResponse(ORMModel):
    request_id: UUID
    ateam_id: UUID
    expiration: datetime
    limit_count: Optional[int] = None
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
    user_id: Optional[UUID] = None
    pteam_id: UUID
    email: str
    executed_at: datetime
    created_at: datetime


class ActionLogRequest(ORMModel):
    action_id: UUID
    topic_id: UUID
    user_id: UUID
    pteam_id: UUID
    executed_at: Optional[datetime] = None


class TopicStatusRequest(ORMModel):
    topic_status: TopicStatusType
    logging_ids: List[UUID] = []
    assignees: List[UUID] = []
    note: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class TopicStatusResponse(ORMModel):
    status_id: Optional[UUID] = None  # None is the case no status is set yet
    topic_id: UUID
    pteam_id: UUID
    tag_id: UUID
    user_id: Optional[UUID] = None
    topic_status: Optional[TopicStatusType] = None
    created_at: Optional[datetime] = None
    assignees: List[UUID] = []
    note: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    action_logs: List[ActionLogResponse] = []


class PTeamTaggedTopics(ORMModel):
    pteam_id: UUID
    tag_id: UUID
    threat_impact_count: Dict[str, int]
    topic_ids: List[UUID]


class PTeamTopicStatusSummary(ORMModel):
    topic_id: UUID
    threat_impact: int
    updated_at: datetime
    topic_status: TopicStatusType
    executed_at: Optional[datetime] = None


class PTeamTopicStatusesSummary(ORMModel):
    tag_id: UUID
    topics: List[PTeamTopicStatusSummary]


class FsAction(ORMModel):
    action_id: UUID
    topic_id: UUID
    action_type: ActionType
    action: str
    recommended: bool


class FsTopicSummary(ORMModel):
    abstract: str
    actions: List[FsAction]


class PTeamTagSummary(ExtTagResponse):
    threat_impact: Optional[int] = None
    updated_at: Optional[datetime] = None
    status_count: Dict[str, int]

    _threat_impact_range = field_validator("threat_impact", mode="before")(threat_impact_range)


class PTeamTagsSummary(ORMModel):
    threat_impact_count: Dict[str, int]  # str(threat_impact): tags count
    tags: List[PTeamTagSummary]


class SlackCheckRequest(ORMModel):
    slack_webhook_url: str


class EmailCheckRequest(ORMModel):
    email: str


class FsServerInfo(ORMModel):
    api_url: str


class PTeamTopicTagStatusSimple(ORMModel):
    topic_id: UUID
    pteam_id: UUID
    tag: TagResponse
    topic_status: TopicStatusType
    assignees: List[UUID] = []
    scheduled_at: Optional[datetime] = None


class PTeamTopicStatuses(ORMModel):
    pteam_id: UUID
    pteam_name: str
    statuses: List[PTeamTopicTagStatusSimple]


class ATeamTopicStatus(ORMModel):
    topic_id: UUID
    title: str
    threat_impact: int
    updated_at: datetime
    num_pteams: int
    pteams: List[PTeamTopicStatuses]


class ATeamTopicStatusResponse(ORMModel):
    num_topics: int
    offset: Optional[int] = None
    limit: Optional[int] = None
    search: Optional[str] = None
    sort_key: str
    topic_statuses: List[ATeamTopicStatus]


class ATeamTopicCommentRequest(ORMModel):
    comment: str


class ATeamTopicCommentResponse(ORMModel):
    comment_id: UUID
    topic_id: UUID
    ateam_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    comment: str
    email: str

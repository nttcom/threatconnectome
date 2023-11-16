from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants import DEFAULT_ALERT_THREAT_IMPACT
from app.models import (
    ActionType,
    ATeamAuthEnum,
    BadgeType,
    CertifierType,
    Difficulty,
    GTeamAuthEnum,
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


class ZoneRequest(ORMModel):
    zone_name: str
    zone_info: str


class ZoneUpdateRequest(ORMModel):
    zone_info: Optional[str] = None


class ZoneUpdateArchivedRequest(ORMModel):
    archived: bool


class ZoneEntry(ORMModel):
    zone_name: str
    zone_info: str
    gteam_id: UUID
    created_by: UUID
    archived: bool


class ZoneInfo(ZoneEntry):
    pass


class User(ORMModel):
    user_id: UUID
    email: str


class TokenData(ORMModel):
    email: str = ""


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
    slack_webhook_url: str
    pteams: List[PTeamEntry]
    zones: List[ZoneEntry]


class GTeamEntry(ORMModel):
    gteam_id: UUID
    gteam_name: str
    contact_info: str


class GTeamInfo(GTeamEntry):
    pass


class BadgeRequest(ORMModel):
    recipient: UUID
    metadata: Dict[str, Any]
    priority: Optional[int] = 100
    difficulty: Optional[Difficulty] = Difficulty["low"]
    badge_type: List[BadgeType]
    certifier_type: CertifierType
    pteam_id: UUID


class SecBadgeBody(ORMModel):
    badge_id: str
    badge_name: str
    image_url: Optional[str] = None
    user_id: UUID
    email: str
    created_by: UUID
    obtained_at: datetime
    created_at: datetime
    expired_at: Optional[datetime] = None
    metadata_json: str
    priority: int
    difficulty: Difficulty
    badge_type: List[BadgeType]
    certifier_type: CertifierType
    pteam_id: UUID


class UserResponse(ORMModel):
    user_id: UUID
    uid: str
    email: str
    disabled: bool
    years: int
    pteams: List[PTeamEntry]
    ateams: List[ATeamEntry]
    gteams: List[GTeamEntry]
    favorite_badge: Optional[UUID] = None


class UserCreateRequest(ORMModel):
    email: str
    uid: str
    years: int = 0


class UserUpdateRequest(ORMModel):
    disabled: Optional[bool] = None
    years: Optional[int] = None
    favorite_badge: Optional[Union[UUID, Literal[""]]] = None


class AuthorizedZones(ORMModel):
    admin: List[ZoneInfo]
    apply: List[ZoneEntry]
    read: List[ZoneEntry]


class ActionResponse(ORMModel):
    topic_id: UUID
    action_id: UUID
    action: str = Field(..., max_length=1024)
    action_type: ActionType
    recommended: bool
    created_by: UUID
    created_at: datetime
    zones: List[ZoneEntry]
    ext: dict  # see ActionCreateRequest


class TagRequest(ORMModel):
    tag_name: str


class ExtTagRequest(TagRequest):
    references: Optional[List[dict]] = []
    text: Optional[str] = None


class TagResponse(ORMModel):
    tag_id: UUID
    tag_name: str
    parent_id: Optional[UUID] = None
    parent_name: Optional[str] = None


class ExtTagResponse(TagResponse):
    references: List[dict] = []
    text: Optional[str] = None

class PTeamGroupResponse(ORMModel):
    groups: List[str] = []


class PTeamtagRequest(ORMModel):
    references: Optional[List[dict]] = None
    text: Optional[str] = None


class PTeamtagResponse(ORMModel):
    pteam_id: UUID
    tag_id: UUID
    references: List[dict]
    text: str


class PTeamtagExtResponse(PTeamtagResponse):
    last_updated_at: Optional[datetime] = None


class TagRegistrationResponse(ORMModel):
    newly_registered_tags: List[ExtTagResponse]
    already_existed_tags: Optional[List[ExtTagRequest]] = None


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
    zones: List[ZoneEntry]


class TopicCreateResponse(TopicResponse):
    actions: List[ActionResponse]


class TopicActionsResponse(ORMModel):
    topic_id: UUID
    pteam_id: UUID
    actions: List[ActionResponse]


class TaggedTopic(Topic):
    latest_status: TopicStatusType


class TaggedTopicsResponse(ORMModel):
    tag_id: UUID
    tag_name: str
    text: Optional[str] = None
    threat_impact: int
    updated_at: datetime
    topics: List[TaggedTopic]

    _threat_impact_range = field_validator("threat_impact", mode="before")(threat_impact_range)


class ActionCreateRequest(ORMModel):
    topic_id: Optional[UUID] = None  # can be None if using in create_topic()
    action_id: Optional[UUID] = None  # can specify action_id by client
    action: str = Field(..., max_length=1024)
    action_type: ActionType
    recommended: bool = False
    zone_names: List[str] = []
    ext: dict = {}
    # {
    #   tags: List[str] = [],
    #   vulnerable_versions: Dict[str, List[dict]] = {},  # see around auto-close for detail.
    # }


class ActionUpdateRequest(ORMModel):
    action: Optional[str] = None
    action_type: Optional[ActionType] = None
    recommended: Optional[bool] = None
    zone_names: Optional[List[str]] = None
    ext: Optional[dict] = None


class TopicCreateRequest(ORMModel):
    title: str
    abstract: str
    threat_impact: int
    tags: List[str] = []
    misp_tags: List[str] = []
    zone_names: List[str] = []
    actions: List[ActionCreateRequest] = []

    _threat_impact_range = field_validator("threat_impact", mode="before")(threat_impact_range)


class TopicUpdateRequest(ORMModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    threat_impact: Optional[int] = None
    tags: Optional[List[str]] = None
    misp_tags: Optional[List[str]] = None
    zone_names: Optional[List[str]] = None
    disabled: Optional[bool] = None

    _threat_impact_range = field_validator("threat_impact", mode="before")(threat_impact_range)


class PTeamInfo(PTeamEntry):
    slack_webhook_url: str
    alert_threat_impact: int
    tags: List[ExtTagResponse] = []
    zones: List[ZoneEntry]
    ateams: List[ATeamEntry]

    _threat_impact_range = field_validator("alert_threat_impact", mode="before")(
        threat_impact_range
    )


class PTeamCreateRequest(ORMModel):
    pteam_name: str
    contact_info: str = ""
    slack_webhook_url: str = ""
    alert_threat_impact: int = DEFAULT_ALERT_THREAT_IMPACT
    tags: List[ExtTagRequest] = []
    zone_names: List[str] = []

    _threat_impact_range = field_validator("alert_threat_impact", mode="before")(
        threat_impact_range
    )


class PTeamUpdateRequest(ORMModel):
    pteam_name: Optional[str] = None
    contact_info: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    alert_threat_impact: Optional[int] = None
    zone_names: Optional[List[str]] = None
    disabled: Optional[bool] = None

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
    slack_webhook_url: str = ""


class ATeamUpdateRequest(ORMModel):
    ateam_name: Optional[str] = None
    contact_info: Optional[str] = None
    slack_webhook_url: Optional[str] = None


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


class GTeamCreateRequest(ORMModel):
    gteam_name: str
    contact_info: str = ""


class GTeamUpdateRequest(ORMModel):
    gteam_name: Optional[str] = None
    contact_info: Optional[str] = None


class GTeamAuthInfo(ORMModel):
    class GTeamAuthEntry(ORMModel):
        enum: str
        name: str
        desc: str

    class PseudoUUID(ORMModel):
        name: str
        uuid: UUID

    authorities: List[GTeamAuthEntry]
    pseudo_uuids: List[PseudoUUID]


class GTeamAuthRequest(ORMModel):
    user_id: UUID
    authorities: List[GTeamAuthEnum]


class GTeamAuthResponse(ORMModel):
    user_id: UUID
    authorities: List[GTeamAuthEnum]


class GTeamInvitationRequest(ORMModel):
    expiration: datetime
    limit_count: Optional[int] = None  # None for unlimited
    authorities: Optional[List[GTeamAuthEnum]] = None  # require ADMIN for not-None


class GTeamInvitationResponse(ORMModel):
    invitation_id: UUID
    gteam_id: UUID
    expiration: datetime
    limit_count: Optional[int] = None
    used_count: int
    authorities: List[GTeamAuthEnum]


class GTeamInviterResponse(ORMModel):
    gteam_id: UUID
    gteam_name: str
    email: str
    user_id: UUID


class ZoneSummary(ZoneEntry):
    pteams: List[PTeamEntry]
    actions: List[ActionResponse]
    topics: List[TopicResponse]


class GTeamZonesSummary(ORMModel):
    unarchived_zones: List[ZoneSummary]
    archived_zones: List[ZoneSummary]


class ZonedTeamsResponse(ORMModel):
    zone: ZoneEntry
    gteam: GTeamEntry
    ateams: List[ATeamEntry]
    pteams: List[PTeamEntry]


class ZonedTopicsResponse(ORMModel):
    zone: ZoneEntry
    gteam: GTeamEntry
    topics: List[TopicEntry]


class ActionResponseWithTopicTitle(ActionResponse):
    topic_title: str


class ZonedActionsResponse(ORMModel):
    zone: ZoneEntry
    gteam: GTeamEntry
    actions: List[ActionResponseWithTopicTitle]


class ZonedLatestTopicResponse(ORMModel):
    zone: ZoneEntry
    gteam: GTeamEntry
    latest_topic: Optional[Topic] = None

import enum
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union, cast

from sqlalchemy import ARRAY, JSON, Enum, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry, relationship
from sqlalchemy.sql.functions import current_timestamp
from typing_extensions import Annotated

# ENUMs


class ActionType(str, enum.Enum):
    elimination = "elimination"
    transfer = "transfer"
    mitigation = "mitigation"
    acceptance = "acceptance"
    detection = "detection"
    rejection = "rejection"


class BadgeType(str, enum.Enum):
    skill = "skill"
    performance = "performance"
    position = "position"


class CertifierType(str, enum.Enum):
    trusted_third_party = "trusted_third_party"
    coworker = "coworker"
    myself = "myself"
    system = "system"


class Difficulty(str, enum.Enum):
    low = "low"
    middle = "middle"
    high = "high"


class PTeamAuthEnum(str, enum.Enum):
    ADMIN = "admin"
    PTEAMBADGE_APPLY = "pteambadge_apply"
    INVITE = "invite"
    PTEAMBADGE_MANAGE = "pteambadge_manage"
    TOPIC_STATUS = "topic_status"

    @classmethod
    def info(cls) -> Dict[str, Dict[str, Union[int, str]]]:
        return {
            "admin": {
                "int": 0,
                "name": "Administrator",
                "desc": "To administrate the pteam.",
            },
            "pteambadge_apply": {
                "int": 1,
                "name": "PTeam badge element",
                "desc": "To be counted in pteam badge.",
            },
            "invite": {
                "int": 2,
                "name": "Inviter",
                "desc": "To create invitation to the pteam.",
            },
            "pteambadge_manage": {
                "int": 3,
                "name": "PTeam badge manager",
                "desc": "To manage pteam member's badge.",
            },
            "topic_status": {
                "int": 4,
                "name": "Topic status operator",
                "desc": "To operate pteam topic status.",
            },
        }

    def to_int(self) -> int:
        return cast(int, PTeamAuthEnum.info()[self.value]["int"])


class PTeamAuthIntFlag(enum.IntFlag):
    """
    Integer which can be combined using the bitwise operators. (INTERNAL USE ONLY!)

    See PTeamAuthEnum.info() for details.
    """

    ADMIN = 1 << PTeamAuthEnum.ADMIN.to_int()
    PTEAMBADGE_APPLY = 1 << PTeamAuthEnum.PTEAMBADGE_APPLY.to_int()
    INVITE = 1 << PTeamAuthEnum.INVITE.to_int()
    PTEAMBADGE_MANAGE = 1 << PTeamAuthEnum.PTEAMBADGE_MANAGE.to_int()
    TOPIC_STATUS = 1 << PTeamAuthEnum.TOPIC_STATUS.to_int()

    # authority sets for members
    PTEAM_MEMBER = TOPIC_STATUS
    PTEAM_LEADER = PTEAM_MEMBER | PTEAMBADGE_APPLY | INVITE | PTEAMBADGE_MANAGE
    PTEAM_MASTER = 0x0FFFFFFF

    # template authority set for non-members
    FREE_TEMPLATE = 0

    @classmethod
    def from_enums(cls, datas: List[PTeamAuthEnum]):
        result = 0
        for data in datas:
            result |= 1 << data.to_int()
        return PTeamAuthIntFlag(result)

    def to_enums(self) -> List[PTeamAuthEnum]:
        result = []
        for data in list(PTeamAuthEnum):
            if self & 1 << data.to_int():
                result.append(data)
        return result


class ATeamAuthEnum(str, enum.Enum):
    ADMIN = "admin"
    INVITE = "invite"

    @classmethod
    def info(cls) -> Dict[str, Dict[str, Union[int, str]]]:
        return {
            "admin": {
                "int": 0,
                "name": "Administrator",
                "desc": "To administrate the ateam.",
            },
            "invite": {
                "int": 1,
                "name": "Inviter",
                "desc": "To create invitation to the ateam.",
            },
        }

    def to_int(self) -> int:
        return cast(int, ATeamAuthEnum.info()[self.value]["int"])


class ATeamAuthIntFlag(enum.IntFlag):
    """
    Integer which can be combined using the bitwise operators. (INTERNAL USE ONLY!)

    See ATeamAuthEnum.info() for details.
    """

    ADMIN = 1 << ATeamAuthEnum.ADMIN.to_int()
    INVITE = 1 << ATeamAuthEnum.INVITE.to_int()

    # authority sets for members
    ATEAM_MEMBER = 0
    ATEAM_LEADER = ATEAM_MEMBER | INVITE
    ATEAM_MASTER = 0x0FFFFFFF

    # template authority set for non-members
    FREE_TEMPLATE = 0

    @classmethod
    def from_enums(cls, datas: List[ATeamAuthEnum]):
        result = 0
        for data in datas:
            result |= 1 << data.to_int()
        return ATeamAuthIntFlag(result)

    def to_enums(self) -> List[ATeamAuthEnum]:
        result = []
        for data in list(ATeamAuthEnum):
            if self & 1 << data.to_int():
                result.append(data)
        return result


class GTeamAuthEnum(str, enum.Enum):
    ADMIN = "admin"
    INVITE = "invite"

    @classmethod
    def info(cls) -> Dict[str, Dict[str, Union[int, str]]]:
        return {
            "admin": {
                "int": 0,
                "name": "Administrator",
                "desc": "To administrate the gteam.",
            },
            "invite": {
                "int": 1,
                "name": "Inviter",
                "desc": "To create invitation to the gteam.",
            },
        }

    def to_int(self) -> int:
        return cast(int, GTeamAuthEnum.info()[self.value]["int"])


class GTeamAuthIntFlag(enum.IntFlag):
    """
    Integer which can be combined using the bitwise operators. (INTERNAL USE ONLY!)

    See GTeamAuthEnum.info() for details.
    """

    ADMIN = 1 << GTeamAuthEnum.ADMIN.to_int()
    INVITE = 1 << GTeamAuthEnum.INVITE.to_int()

    # authority sets for members
    GTEAM_MEMBER = 0
    GTEAM_MASTER = 0x0FFFFFFF

    # template authority set for non-members
    FREE_TEMPLATE = 0

    @classmethod
    def from_enums(cls, datas: List[GTeamAuthEnum]):
        result = 0
        for data in datas:
            result |= 1 << data.to_int()
        return GTeamAuthIntFlag(result)

    def to_enums(self) -> List[GTeamAuthEnum]:
        result = []
        for data in list(GTeamAuthEnum):
            if self & 1 << data.to_int():
                result.append(data)
        return result


class TopicStatusType(str, enum.Enum):
    alerted = "alerted"
    acknowledged = "acknowledged"
    scheduled = "scheduled"
    completed = "completed"


# Base class

StrUUID = Annotated[str, 36]
Str255 = Annotated[str, 255]


class Base(DeclarativeBase):
    registry = registry(
        type_annotation_map={
            str: Text,
            StrUUID: String(36),
            Str255: String(255),
            dict: JSON,
            List[dict]: ARRAY(JSON),
            List[StrUUID]: ARRAY(String(36)),
            List[BadgeType]: ARRAY(Enum(BadgeType)),
        }
    )


# secondary tables #


class PTeamZone(Base):
    __tablename__ = "pteamzone"

    pteam_id = mapped_column(ForeignKey("pteam.pteam_id"), primary_key=True, index=True)
    zone_name = mapped_column(ForeignKey("zone.zone_name"), primary_key=True, index=True)


class PTeamAccount(Base):
    __tablename__ = "pteamaccount"

    pteam_id = mapped_column(ForeignKey("pteam.pteam_id"), primary_key=True, index=True)
    user_id = mapped_column(ForeignKey("account.user_id"), primary_key=True, index=True)


class ATeamAccount(Base):
    __tablename__ = "ateamaccount"

    ateam_id = mapped_column(ForeignKey("ateam.ateam_id"), primary_key=True, index=True)
    user_id = mapped_column(ForeignKey("account.user_id"), primary_key=True, index=True)


class GTeamAccount(Base):
    __tablename__ = "gteamaccount"

    gteam_id = mapped_column(ForeignKey("gteam.gteam_id"), primary_key=True, index=True)
    user_id = mapped_column(ForeignKey("account.user_id"), primary_key=True, index=True)


class ATeamPTeam(Base):
    __tablename__ = "ateampteam"

    ateam_id = mapped_column(ForeignKey("ateam.ateam_id"), primary_key=True, index=True)
    pteam_id = mapped_column(ForeignKey("pteam.pteam_id"), primary_key=True, index=True)


class TopicTag(Base):
    __tablename__ = "topictag"

    topic_id = mapped_column(
        ForeignKey("topic.topic_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    tag_id = mapped_column(
        ForeignKey("tag.tag_id", ondelete="CASCADE"), primary_key=True, index=True
    )


class TopicMispTag(Base):
    __tablename__ = "topicmisptag"

    topic_id = mapped_column(
        ForeignKey("topic.topic_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    tag_id = mapped_column(
        ForeignKey("misptag.tag_id", ondelete="CASCADE"), primary_key=True, index=True
    )


class TopicZone(Base):
    __tablename__ = "topiczone"

    topic_id = mapped_column(
        ForeignKey("topic.topic_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    zone_name = mapped_column(
        ForeignKey("zone.zone_name", ondelete="CASCADE"), primary_key=True, index=True
    )


class ActionZone(Base):
    __tablename__ = "actionzone"

    action_id = mapped_column(ForeignKey("topicaction.action_id"), primary_key=True, index=True)
    zone_name = mapped_column(ForeignKey("zone.zone_name"), primary_key=True, index=True)


# primary tables #


class Account(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.user_id:
            self.user_id = str(uuid.uuid4())

    __tablename__ = "account"

    user_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    uid: Mapped[Optional[str]] = mapped_column(unique=True)  # UID on Firebase
    email: Mapped[Optional[Str255]]
    disabled: Mapped[bool] = mapped_column(default=False)
    years: Mapped[Optional[int]]
    favorite_badge: Mapped[Optional[StrUUID]] = mapped_column(
        ForeignKey("secbadge.badge_id", use_alter=True), index=True
    )

    pteams = relationship("PTeam", secondary=PTeamAccount.__tablename__, back_populates="members")
    ateams = relationship("ATeam", secondary=ATeamAccount.__tablename__, back_populates="members")
    gteams = relationship("GTeam", secondary=GTeamAccount.__tablename__, back_populates="members")
    pteam_invitations = relationship("PTeamInvitation", back_populates="inviter")
    ateam_invitations = relationship("ATeamInvitation", back_populates="inviter")
    gteam_invitations = relationship("GTeamInvitation", back_populates="inviter")
    ateam_requests = relationship("ATeamWatchingRequest", back_populates="requester")
    action_logs = relationship("ActionLog", back_populates="executed_by")


class PTeamTagReference(Base):
    __tablename__ = "pteamtagreference"

    pteam_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("pteam.pteam_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    tag_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("tag.tag_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    group: Mapped[Str255] = mapped_column(primary_key=True, index=True)
    target: Mapped[str] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(primary_key=True)

    pteam = relationship("PTeam", back_populates="references")
    tag = relationship("Tag", back_populates="references")


class PTeam(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.pteam_id:
            self.pteam_id = str(uuid.uuid4())

    __tablename__ = "pteam"

    pteam_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    pteam_name: Mapped[Str255]
    contact_info: Mapped[Str255]
    alert_threat_impact: Mapped[Optional[int]]
    disabled: Mapped[bool] = mapped_column(default=False)

    references = relationship(
        "PTeamTagReference", back_populates="pteam", cascade="all, delete-orphan"
    )
    zones = relationship("Zone", secondary=PTeamZone.__tablename__, back_populates="pteams")
    members = relationship("Account", secondary=PTeamAccount.__tablename__, back_populates="pteams")
    invitations = relationship("PTeamInvitation", back_populates="pteam")
    ateams = relationship("ATeam", secondary=ATeamPTeam.__tablename__, back_populates="pteams")
    alert_slack: Mapped["PTeamSlack"] = relationship(
        back_populates="pteam", cascade="all, delete-orphan"
    )
    alert_mail: Mapped["PTeamMail"] = relationship(
        back_populates="pteam", cascade="all, delete-orphan"
    )


class ATeam(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.ateam_id:
            self.ateam_id = str(uuid.uuid4())

    __tablename__ = "ateam"

    ateam_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    ateam_name: Mapped[Str255]
    contact_info: Mapped[Str255]
    members = relationship("Account", secondary=ATeamAccount.__tablename__, back_populates="ateams")
    invitations = relationship("ATeamInvitation", back_populates="ateam")
    pteams = relationship("PTeam", secondary=ATeamPTeam.__tablename__, back_populates="ateams")
    watching_requests = relationship("ATeamWatchingRequest", back_populates="ateam")
    alert_slack: Mapped["ATeamSlack"] = relationship(
        back_populates="ateam", cascade="all, delete-orphan"
    )
    alert_mail: Mapped["ATeamMail"] = relationship(
        back_populates="ateam", cascade="all, delete-orphan"
    )


class GTeam(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.gteam_id:
            self.gteam_id = str(uuid.uuid4())

    __tablename__ = "gteam"

    gteam_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    gteam_name: Mapped[Str255]
    contact_info: Mapped[Str255]

    members = relationship("Account", secondary=GTeamAccount.__tablename__, back_populates="gteams")
    invitations = relationship("GTeamInvitation", back_populates="gteam")
    zones = relationship("Zone", back_populates="gteam")


# TODO: This info should be stored in PTeamAccount table to cascade delete
class PTeamAuthority(Base):
    __tablename__ = "pteamauthority"

    pteam_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("pteam.pteam_id"), primary_key=True, index=True
    )
    user_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("account.user_id"), primary_key=True, index=True
    )
    authority: Mapped[int]  # PTeamAuthIntFlag as an integer


# TODO: This info should be stored in ATeamAccount table to cascade delete
class ATeamAuthority(Base):
    __tablename__ = "ateamauthority"

    ateam_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("ateam.ateam_id"), primary_key=True, index=True
    )
    user_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("account.user_id"), primary_key=True, index=True
    )
    authority: Mapped[int]  # ATeamAuthIntFlag as an integer


# TODO: This info should be stored in GTeamAccount table to cascade delete
class GTeamAuthority(Base):
    __tablename__ = "gteamauthority"

    gteam_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("gteam.gteam_id"), primary_key=True, index=True
    )
    user_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("account.user_id"), primary_key=True, index=True
    )
    authority: Mapped[int]  # GTeamAuthIntFlag as an integer


class PTeamMail(Base):
    __tablename__ = "pteammail"

    pteam_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("pteam.pteam_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    enable: Mapped[bool]
    address: Mapped[Str255]

    pteam: Mapped[PTeam] = relationship(back_populates="alert_mail")


class ATeamMail(Base):
    __tablename__ = "ateammail"

    ateam_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("ateam.ateam_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    enable: Mapped[bool]
    address: Mapped[Str255]

    ateam: Mapped[ATeam] = relationship(back_populates="alert_mail")


class PTeamSlack(Base):
    __tablename__ = "pteamslack"

    pteam_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("pteam.pteam_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    enable: Mapped[bool] = mapped_column(default=True)
    webhook_url: Mapped[Str255]

    pteam: Mapped[PTeam] = relationship(back_populates="alert_slack")


class ATeamSlack(Base):
    __tablename__ = "ateamslack"

    ateam_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("ateam.ateam_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    enable: Mapped[bool] = mapped_column(default=True)
    webhook_url: Mapped[Str255]

    ateam: Mapped[ATeam] = relationship(back_populates="alert_slack")


class SecBadge(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.badge_id:
            self.badge_id = str(uuid.uuid4())

    __tablename__ = "secbadge"

    badge_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    badge_name: Mapped[Str255]
    image_url: Mapped[Str255]
    user_id: Mapped[StrUUID] = mapped_column(ForeignKey("account.user_id"), index=True)
    email: Mapped[Str255]
    created_by: Mapped[StrUUID] = mapped_column(ForeignKey("account.user_id"), index=True)
    obtained_at: Mapped[datetime]
    created_at: Mapped[datetime]
    expired_at: Mapped[Optional[datetime]]
    metadata_json: Mapped[dict]
    priority: Mapped[int] = mapped_column(default=100)
    difficulty: Mapped[Difficulty] = mapped_column(default="low")
    badge_type: Mapped[List[BadgeType]]
    certifier_type: Mapped[CertifierType]
    pteam_id: Mapped[StrUUID] = mapped_column(ForeignKey("pteam.pteam_id"), index=True)


class Topic(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.topic_id:
            self.topic_id = str(uuid.uuid4())

    __tablename__ = "topic"

    topic_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    title: Mapped[Str255]
    abstract: Mapped[str]
    threat_impact: Mapped[int]
    created_by: Mapped[StrUUID] = mapped_column(ForeignKey("account.user_id"), index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(server_default=current_timestamp())
    content_fingerprint: Mapped[str]
    disabled: Mapped[bool] = mapped_column(default=False)

    actions = relationship("TopicAction", back_populates="topic", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=TopicTag.__tablename__, order_by="Tag.tag_name")
    misp_tags = relationship(
        "MispTag", secondary=TopicMispTag.__tablename__, order_by="MispTag.tag_name"
    )
    zones = relationship("Zone", secondary=TopicZone.__tablename__, order_by="Zone.zone_name")


class TopicAction(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.action_id:
            self.action_id = str(uuid.uuid4())

    __tablename__ = "topicaction"

    action_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    topic_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("topic.topic_id", ondelete="CASCADE"), index=True
    )
    action: Mapped[str]
    action_type: Mapped[ActionType] = mapped_column(default=ActionType.elimination)
    recommended: Mapped[bool] = mapped_column(default=False)
    ext: Mapped[dict] = mapped_column(default={})
    created_by: Mapped[StrUUID] = mapped_column(ForeignKey("account.user_id"), index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=current_timestamp())

    zones = relationship("Zone", secondary=ActionZone.__tablename__, order_by="Zone.zone_name")
    topic = relationship("Topic", back_populates="actions")


class PTeamTopicTagStatus(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.status_id:
            self.status_id = str(uuid.uuid4())

    __tablename__ = "pteamtopictagstatus"

    status_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    pteam_id: Mapped[StrUUID] = mapped_column(ForeignKey("pteam.pteam_id"), index=True)
    topic_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("topic.topic_id", ondelete="CASCADE"), index=True
    )
    tag_id: Mapped[StrUUID] = mapped_column(ForeignKey("tag.tag_id"), index=True)
    user_id: Mapped[StrUUID] = mapped_column(ForeignKey("account.user_id"), index=True)
    topic_status: Mapped[TopicStatusType]
    note: Mapped[Optional[str]]
    logging_ids: Mapped[List[StrUUID]] = mapped_column(default=[])
    assignees: Mapped[List[StrUUID]] = mapped_column(default=[])
    scheduled_at: Mapped[Optional[datetime]]
    created_at: Mapped[datetime] = mapped_column(server_default=current_timestamp())


class CurrentPTeamTopicTagStatus(Base):
    __tablename__ = "currentpteamtopictagstatus"

    pteam_id: Mapped[StrUUID] = mapped_column(
        "pteam_id", ForeignKey("pteam.pteam_id"), primary_key=True, index=True
    )
    topic_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("topic.topic_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    tag_id: Mapped[StrUUID] = mapped_column(ForeignKey("tag.tag_id"), primary_key=True, index=True)
    status_id: Mapped[Optional[StrUUID]] = mapped_column(
        ForeignKey("pteamtopictagstatus.status_id"), index=True
    )
    topic_status: Mapped[Optional[TopicStatusType]]
    threat_impact: Mapped[Optional[int]]
    updated_at: Mapped[Optional[datetime]]

    pteam = relationship("PTeam")
    topic = relationship("Topic")
    tag = relationship("Tag")


class Tag(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.tag_id:
            self.tag_id = str(uuid.uuid4())

    __tablename__ = "tag"

    tag_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    tag_name: Mapped[str] = mapped_column(unique=True)
    parent_id: Mapped[Optional[StrUUID]] = mapped_column(ForeignKey("tag.tag_id"), index=True)
    parent_name: Mapped[Optional[str]] = mapped_column(ForeignKey("tag.tag_name"), index=True)

    topics = relationship("Topic", secondary=TopicTag.__tablename__, back_populates="tags")
    references = relationship(
        "PTeamTagReference", back_populates="tag", cascade="all, delete-orphan"
    )


class MispTag(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.tag_id:
            self.tag_id = str(uuid.uuid4())

    __tablename__ = "misptag"

    tag_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    tag_name: Mapped[str]

    topics = relationship("Topic", secondary=TopicMispTag.__tablename__, back_populates="misp_tags")


class Zone(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    __tablename__ = "zone"

    zone_name: Mapped[Str255] = mapped_column(primary_key=True)
    zone_info: Mapped[str]
    gteam_id: Mapped[StrUUID] = mapped_column(ForeignKey("gteam.gteam_id"), index=True)
    created_by: Mapped[StrUUID] = mapped_column(ForeignKey("account.user_id"), index=True)
    archived: Mapped[bool]

    gteam = relationship("GTeam", back_populates="zones")
    pteams = relationship("PTeam", secondary=PTeamZone.__tablename__, back_populates="zones")
    topics = relationship("Topic", secondary=TopicZone.__tablename__, back_populates="zones")
    actions = relationship(
        "TopicAction",
        secondary=ActionZone.__tablename__,
        back_populates="zones",
    )


class ActionLog(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.logging_id:
            self.logging_id = str(uuid.uuid4())

    __tablename__ = "actionlog"

    logging_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    action_id: Mapped[StrUUID]  # snapshot: don't set ForeignKey.
    topic_id: Mapped[StrUUID]  # snapshot: don't set ForeignKey.
    action: Mapped[str]  # snapshot: don't update even if TopicAction is modified.
    action_type: Mapped[ActionType]
    recommended: Mapped[bool]  # snapshot: don't update even if TopicAction is modified.
    user_id: Mapped[Optional[StrUUID]] = mapped_column(ForeignKey("account.user_id"), index=True)
    pteam_id: Mapped[StrUUID] = mapped_column(ForeignKey("pteam.pteam_id"), index=True)
    email: Mapped[Str255]  # snapshot: don't set ForeignKey.
    executed_at: Mapped[datetime] = mapped_column(server_default=current_timestamp())
    created_at: Mapped[datetime] = mapped_column(server_default=current_timestamp())

    executed_by = relationship("Account", back_populates="action_logs")


class PTeamInvitation(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.invitation_id:
            self.invitation_id = str(uuid.uuid4())

    __tablename__ = "pteaminvitation"

    invitation_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    pteam_id: Mapped[StrUUID] = mapped_column(ForeignKey("pteam.pteam_id"), index=True)
    user_id: Mapped[StrUUID] = mapped_column(ForeignKey("account.user_id"), index=True)
    expiration: Mapped[datetime]
    limit_count: Mapped[Optional[int]]  # None for unlimited
    used_count: Mapped[int] = mapped_column(server_default="0")
    authority: Mapped[int]  # PTeamAuthIntFlag

    pteam = relationship("PTeam", back_populates="invitations")
    inviter = relationship("Account", back_populates="pteam_invitations")


class ATeamInvitation(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.invitation_id:
            self.invitation_id = str(uuid.uuid4())

    __tablename__ = "ateaminvitation"

    invitation_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    ateam_id: Mapped[StrUUID] = mapped_column(ForeignKey("ateam.ateam_id"), index=True)
    user_id: Mapped[StrUUID] = mapped_column(ForeignKey("account.user_id"), index=True)
    expiration: Mapped[datetime]
    limit_count: Mapped[Optional[int]]  # None for unlimited
    used_count: Mapped[int] = mapped_column(server_default="0")
    authority: Mapped[int]  # ATeamAuthIntFlag

    ateam = relationship("ATeam", back_populates="invitations")
    inviter = relationship("Account", back_populates="ateam_invitations")


class GTeamInvitation(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.invitation_id:
            self.invitation_id = str(uuid.uuid4())

    __tablename__ = "gteaminvitation"

    invitation_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    gteam_id: Mapped[StrUUID] = mapped_column(ForeignKey("gteam.gteam_id"), index=True)
    user_id: Mapped[StrUUID] = mapped_column(ForeignKey("account.user_id"), index=True)
    expiration: Mapped[datetime]
    limit_count: Mapped[Optional[int]]  # None for unlimited
    used_count: Mapped[int] = mapped_column(server_default="0")
    authority: Mapped[int]  # GTeamAuthIntFlag

    gteam = relationship("GTeam", back_populates="invitations")
    inviter = relationship("Account", back_populates="gteam_invitations")


class ATeamWatchingRequest(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.request_id:
            self.request_id = str(uuid.uuid4())

    __tablename__ = "ateamwatchingrequest"

    request_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    ateam_id: Mapped[StrUUID] = mapped_column(ForeignKey("ateam.ateam_id"), index=True)
    user_id: Mapped[StrUUID] = mapped_column(ForeignKey("account.user_id"), index=True)
    expiration: Mapped[datetime]
    limit_count: Mapped[Optional[int]]  # None for unlimited
    used_count: Mapped[int] = mapped_column(server_default="0")

    ateam = relationship("ATeam", back_populates="watching_requests")
    requester = relationship("Account", back_populates="ateam_requests")


class ATeamTopicComment(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.comment_id:
            self.comment_id = str(uuid.uuid4())

    __tablename__ = "ateamtopiccomment"

    comment_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    topic_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("topic.topic_id", ondelete="CASCADE"), index=True
    )
    ateam_id: Mapped[StrUUID] = mapped_column(ForeignKey("ateam.ateam_id"), index=True)
    user_id: Mapped[StrUUID] = mapped_column(ForeignKey("account.user_id"), index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=current_timestamp())
    updated_at: Mapped[Optional[datetime]]
    comment: Mapped[str]

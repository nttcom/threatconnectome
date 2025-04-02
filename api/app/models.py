import enum
import uuid
from datetime import datetime

from sqlalchemy import ARRAY, JSON, ForeignKey, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry, relationship
from sqlalchemy.sql.expression import join, outerjoin
from sqlalchemy.sql.functions import current_timestamp
from typing_extensions import Annotated

# ENUMs


class ComparableStringEnum(str, enum.Enum):

    @property
    # Note: this method can be a classmethod in python3.10, but chaining classmethod descriptors
    #       is depricated in python3.11.
    def _orders_map(self):
        # Note: list(Enum) returns enums in definition order.
        #       see enum.EnumMeta.__iter__()
        return {element.value: index for index, element in enumerate(self.__class__)}

    def _comparable(self, other):
        return isinstance(other, self.__class__)

    def __lt__(self, other):
        if not self._comparable(other):
            return NotImplemented
        return self._orders_map[self] < self._orders_map[other]

    def __le__(self, other):
        if not self._comparable(other):
            return NotImplemented
        return self._orders_map[self] <= self._orders_map[other]

    def __gt__(self, other):
        if not self._comparable(other):
            return NotImplemented
        return self._orders_map[self] > self._orders_map[other]

    def __ge__(self, other):
        if not self._comparable(other):
            return NotImplemented
        return self._orders_map[self] >= self._orders_map[other]


class ActionType(str, enum.Enum):
    elimination = "elimination"
    transfer = "transfer"
    mitigation = "mitigation"
    acceptance = "acceptance"
    detection = "detection"
    rejection = "rejection"


class TopicStatusType(str, enum.Enum):
    alerted = "alerted"
    acknowledged = "acknowledged"
    scheduled = "scheduled"
    completed = "completed"


class AutomatableEnum(str, enum.Enum):
    # https://certcc.github.io/SSVC/reference/decision_points/automatable/
    # Automatable v2.0.0
    YES = "yes"
    NO = "no"


class ExploitationEnum(str, enum.Enum):
    # https://certcc.github.io/SSVC/reference/decision_points/exploitation/
    # Exploitation v1.1.0
    ACTIVE = "active"
    PUBLIC_POC = "public_poc"
    NONE = "none"


class SystemExposureEnum(str, enum.Enum):
    # https://certcc.github.io/SSVC/reference/decision_points/system_exposure/
    # System Exposure v1.0.1
    OPEN = "open"
    CONTROLLED = "controlled"
    SMALL = "small"


class SafetyImpactEnum(str, enum.Enum):
    # https://certcc.github.io/SSVC/reference/decision_points/safety_impact/
    # Safety Impact v2.0.0
    # see also,
    # https://certcc.github.io/SSVC/reference/decision_points/human_impact/
    # Human Impact v2.0.1
    CATASTROPHIC = "catastrophic"
    CRITICAL = "critical"
    MARGINAL = "marginal"
    NEGLIGIBLE = "negligible"


class MissionImpactEnum(str, enum.Enum):
    # https://certcc.github.io/SSVC/reference/decision_points/mission_impact/
    # Mission Impact v2.0.0
    MISSION_FAILURE = "mission_failure"
    MEF_FAILURE = "mef_failure"
    MEF_SUPPORT_CRIPPLED = "mef_support_crippled"
    DEGRADED = "degraded"


class HumanImpactEnum(str, enum.Enum):
    # https://certcc.github.io/SSVC/reference/decision_points/human_impact/
    # Human Impact v2.0.1
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class SSVCDeployerPriorityEnum(ComparableStringEnum):
    # https://certcc.github.io/SSVC/howto/deployer_tree/#deployer-decision-outcomes
    IMMEDIATE = "immediate"
    OUT_OF_CYCLE = "out_of_cycle"
    SCHEDULED = "scheduled"
    DEFER = "defer"


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
            list[dict]: ARRAY(JSON),
            list[StrUUID]: ARRAY(String(36)),
            list[Str255]: ARRAY(String(255)),
            bytes: LargeBinary(),
        }
    )


# secondary tables #


class PTeamAccountRole(Base):
    __tablename__ = "pteamaccountrole"
    # deleting PTeamAccountRole via relationship may cause SAWarning,
    #   "DELETE statement on table 'pteamaccountrole' expected to delete 2 row(s); 1 were matched."
    # set False to confirm_deleted_rows to prevent this warning.
    __mapper_args__ = {"confirm_deleted_rows": False}

    pteam_id = mapped_column(
        ForeignKey("pteam.pteam_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    user_id = mapped_column(
        ForeignKey("account.user_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    is_admin: Mapped[bool] = mapped_column(default=False)

    pteam = relationship("PTeam", back_populates="pteam_roles", uselist=False)
    account = relationship("Account", back_populates="pteam_roles", uselist=False)


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


# primary tables #


class Account(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.user_id:
            self.user_id = str(uuid.uuid4())

    __tablename__ = "account"

    user_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    uid: Mapped[str | None] = mapped_column(unique=True)
    email: Mapped[Str255 | None]
    disabled: Mapped[bool] = mapped_column(default=False)
    years: Mapped[int | None]

    pteam_invitations = relationship("PTeamInvitation", back_populates="inviter")
    action_logs = relationship("ActionLog", back_populates="executed_by")
    pteam_roles = relationship(
        "PTeamAccountRole", back_populates="account", cascade="all, delete-orphan"
    )


class Dependency(Base):
    __tablename__ = "dependency"
    __table_args__: tuple = (
        UniqueConstraint(
            "service_id",
            "tag_id",
            "version",
            "target",
            name="dependency_service_id_tag_id_version_target_key",
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.dependency_id:
            self.dependency_id = str(uuid.uuid4())

    dependency_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    service_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("service.service_id", ondelete="CASCADE"), index=True
    )
    tag_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("tag.tag_id", ondelete="CASCADE"), index=True
    )
    version: Mapped[str]
    target: Mapped[str]
    dependency_mission_impact: Mapped[MissionImpactEnum | None] = mapped_column(
        server_default=None, nullable=True
    )

    service = relationship("Service", back_populates="dependencies")
    tag = relationship("Tag", back_populates="dependencies")
    threats = relationship("Threat", back_populates="dependency", cascade="all, delete-orphan")


class Service(Base):
    __tablename__ = "service"
    __table_args__: tuple = (
        UniqueConstraint("pteam_id", "service_name", name="service_pteam_id_service_name_key"),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.service_id:
            self.service_id = str(uuid.uuid4())
        if not self.system_exposure:
            self.system_exposure = SystemExposureEnum.OPEN
        if not self.service_mission_impact:
            self.service_mission_impact = MissionImpactEnum.MISSION_FAILURE
        if not self.service_safety_impact:
            self.service_safety_impact = SafetyImpactEnum.NEGLIGIBLE

    service_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    pteam_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("pteam.pteam_id", ondelete="CASCADE"), index=True
    )
    service_name: Mapped[Str255]
    system_exposure: Mapped[SystemExposureEnum] = mapped_column(
        server_default=SystemExposureEnum.OPEN
    )
    service_mission_impact: Mapped[MissionImpactEnum] = mapped_column(
        server_default=MissionImpactEnum.MISSION_FAILURE
    )
    service_safety_impact: Mapped[SafetyImpactEnum] = mapped_column(
        server_default=SafetyImpactEnum.NEGLIGIBLE
    )
    sbom_uploaded_at: Mapped[datetime | None]
    description: Mapped[str | None]
    keywords: Mapped[list[Str255]] = mapped_column(server_default="{}")

    pteam = relationship("PTeam", back_populates="services")
    dependencies = relationship(
        "Dependency", back_populates="service", cascade="all, delete-orphan"
    )
    thumbnail = relationship("ServiceThumbnail", uselist=False, cascade="all, delete-orphan")
    tickets = relationship(  # Service - [ Dependency - Threat ] - Ticket
        "Ticket",
        secondary="join(Dependency, Threat, Dependency.dependency_id == Threat.dependency_id)",
        collection_class=set,
        viewonly=True,
    )


class ServiceThumbnail(Base):
    __tablename__ = "servicethumbnail"

    service_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("service.service_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    media_type: Mapped[Str255]
    image_data: Mapped[bytes]


class Threat(Base):
    __tablename__ = "threat"
    __table_args__ = (
        UniqueConstraint("dependency_id", "topic_id", name="threat_dependency_id_topic_id_key"),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.threat_id:
            self.threat_id = str(uuid.uuid4())

    threat_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    threat_safety_impact: Mapped[SafetyImpactEnum | None] = mapped_column(nullable=True)
    reason_safety_impact: Mapped[str | None]
    dependency_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("dependency.dependency_id", ondelete="CASCADE"), index=True
    )
    topic_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("topic.topic_id", ondelete="CASCADE"), index=True
    )

    topic = relationship("Topic", back_populates="threats")
    ticket = relationship("Ticket", uselist=False, back_populates="threat", cascade="all, delete")
    dependency = relationship("Dependency", uselist=False, back_populates="threats")


class Ticket(Base):
    __tablename__ = "ticket"

    def __init__(self, *args, **kwargs) -> None:
        now = datetime.now()
        super().__init__(*args, **kwargs)
        if not self.ticket_id:
            self.ticket_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = now

    ticket_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    threat_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("threat.threat_id", ondelete="CASCADE"), index=True, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=current_timestamp())
    ssvc_deployer_priority: Mapped[SSVCDeployerPriorityEnum | None] = mapped_column(nullable=True)

    threat = relationship("Threat", back_populates="ticket")
    alerts = relationship("Alert", back_populates="ticket")
    ticket_status = relationship("TicketStatus", uselist=False, cascade="all, delete-orphan")


class TicketStatus(Base):
    __tablename__ = "ticketstatus"

    def __init__(self, *args, **kwargs) -> None:
        now = datetime.now()
        super().__init__(*args, **kwargs)
        if not self.status_id:
            self.status_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = now

    status_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    ticket_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("ticket.ticket_id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[StrUUID | None] = mapped_column(
        ForeignKey("account.user_id", ondelete="SET NULL"), index=True
    )
    topic_status: Mapped[TopicStatusType]
    note: Mapped[str | None]
    logging_ids: Mapped[list[StrUUID]] = mapped_column(default=[])
    assignees: Mapped[list[StrUUID]] = mapped_column(default=[])
    scheduled_at: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(server_default=current_timestamp())

    action_logs = relationship(
        "ActionLog",
        primaryjoin="TicketStatus.logging_ids.any(foreign(ActionLog.logging_id))",
        collection_class=set,
        viewonly=True,
    )


class Alert(Base):
    __tablename__ = "alert"

    def __init__(self, *args, **kwargs) -> None:
        now = datetime.now()
        super().__init__(*args, **kwargs)
        if not self.alert_id:
            self.alert_id = str(uuid.uuid4())
        if not self.alerted_at:
            self.alerted_at = now

    alert_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    ticket_id: Mapped[StrUUID | None] = mapped_column(
        ForeignKey("ticket.ticket_id", ondelete="SET NULL"), index=True, nullable=True
    )
    alerted_at: Mapped[datetime] = mapped_column(server_default=current_timestamp())
    alert_content: Mapped[str | None] = mapped_column(nullable=True)  # WORKAROUND

    ticket = relationship("Ticket", back_populates="alerts")


class PTeam(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.pteam_id:
            self.pteam_id = str(uuid.uuid4())
        if not self.alert_ssvc_priority:
            self.alert_ssvc_priority = SSVCDeployerPriorityEnum.IMMEDIATE

    __tablename__ = "pteam"

    pteam_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    pteam_name: Mapped[Str255]
    contact_info: Mapped[Str255]
    alert_ssvc_priority: Mapped[SSVCDeployerPriorityEnum] = mapped_column(
        server_default=SSVCDeployerPriorityEnum.IMMEDIATE
    )

    tags = relationship(  # PTeam - [Service - Dependency] - Tag
        "Tag",  # right most table is Tag
        # secondary table is a joined table -- Service.join(Dependency)
        secondary=join(Service, Dependency, Service.service_id == Dependency.service_id),
        # left join condition : for PTeam.join(SecondaryTable)
        #   declare with string because PTeam table is not yet defined
        primaryjoin="PTeam.pteam_id == Service.pteam_id",
        # right join condition : for SecondaryTable.join(Tag)
        #   declare with string because Tag table is not yet defined
        secondaryjoin="Dependency.tag_id == Tag.tag_id",
        collection_class=set,  # avoid duplications
        viewonly=True,  # block updating via this relationship
    )
    services = relationship(
        "Service",
        order_by="Service.service_name",
        back_populates="pteam",
        cascade="all, delete-orphan",
    )
    # set members viewonly to prevent confliction with pream_roles.
    # to update members, update pteam_foles instead.
    members = relationship("Account", secondary=PTeamAccountRole.__tablename__, viewonly=True)
    pteam_roles = relationship(
        "PTeamAccountRole", back_populates="pteam", cascade="all, delete-orphan"
    )
    invitations = relationship(
        "PTeamInvitation", back_populates="pteam", cascade="all, delete-orphan"
    )
    alert_slack: Mapped["PTeamSlack"] = relationship(
        back_populates="pteam", cascade="all, delete-orphan"
    )
    alert_mail: Mapped["PTeamMail"] = relationship(
        back_populates="pteam", cascade="all, delete-orphan"
    )


class PTeamMail(Base):
    __tablename__ = "pteammail"

    pteam_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("pteam.pteam_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    enable: Mapped[bool]
    address: Mapped[Str255]

    pteam: Mapped[PTeam] = relationship(back_populates="alert_mail")


class PTeamSlack(Base):
    __tablename__ = "pteamslack"

    pteam_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("pteam.pteam_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    enable: Mapped[bool] = mapped_column(default=True)
    webhook_url: Mapped[Str255]

    pteam: Mapped[PTeam] = relationship(back_populates="alert_slack")


class Tag(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.tag_id:
            self.tag_id = str(uuid.uuid4())

    __tablename__ = "tag"

    tag_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    tag_name: Mapped[str] = mapped_column(unique=True)
    parent_id: Mapped[StrUUID | None] = mapped_column(ForeignKey("tag.tag_id"), index=True)
    parent_name: Mapped[str | None] = mapped_column(ForeignKey("tag.tag_name"), index=True)

    topics = relationship(
        "Topic",
        secondary=TopicTag.__tablename__,
        primaryjoin="TopicTag.tag_id.in_([Tag.tag_id, Tag.parent_id])",
        collection_class=set,
        viewonly=True,
    )
    dependencies = relationship("Dependency", back_populates="tag", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topic"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.topic_id:
            self.topic_id = str(uuid.uuid4())
        if not self.exploitation:
            self.exploitation = ExploitationEnum.NONE
        if not self.automatable:
            self.automatable = AutomatableEnum.NO

    topic_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    title: Mapped[Str255]
    abstract: Mapped[str]
    cve_id: Mapped[str | None] = mapped_column(nullable=True)
    created_by: Mapped[StrUUID | None] = mapped_column(
        ForeignKey("account.user_id", ondelete="SET NULL"), index=True, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(server_default=current_timestamp())
    content_fingerprint: Mapped[str]
    exploitation: Mapped[ExploitationEnum] = mapped_column(server_default=ExploitationEnum.NONE)
    automatable: Mapped[AutomatableEnum] = mapped_column(server_default=AutomatableEnum.NO)
    cvss_v3_score: Mapped[float | None] = mapped_column(server_default=None, nullable=True)

    actions = relationship("TopicAction", back_populates="topic", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=TopicTag.__tablename__, order_by="Tag.tag_name")
    misp_tags = relationship(
        "MispTag", secondary=TopicMispTag.__tablename__, order_by="MispTag.tag_name"
    )
    threats = relationship("Threat", back_populates="topic", cascade="all, delete-orphan")
    dependencies_via_tag = relationship(  # dependencies which have one of topic tag (or child)
        Dependency,  # Topic - [TopicTag - Tag] - Dependency
        secondary=outerjoin(TopicTag, Tag, TopicTag.tag_id.in_([Tag.tag_id, Tag.parent_id])),
        primaryjoin="Topic.topic_id == TopicTag.topic_id",
        secondaryjoin="Tag.tag_id == Dependency.tag_id",
        collection_class=set,
        viewonly=True,
    )


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
    created_by: Mapped[StrUUID | None] = mapped_column(
        ForeignKey("account.user_id", ondelete="SET NULL"), index=True, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=current_timestamp())

    topic = relationship("Topic", back_populates="actions")


class MispTag(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.tag_id:
            self.tag_id = str(uuid.uuid4())

    __tablename__ = "misptag"

    tag_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    tag_name: Mapped[str]

    topics = relationship("Topic", secondary=TopicMispTag.__tablename__, back_populates="misp_tags")


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
    user_id: Mapped[StrUUID | None] = mapped_column(
        ForeignKey("account.user_id", ondelete="SET NULL"), index=True
    )
    pteam_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("pteam.pteam_id", ondelete="CASCADE"), index=True
    )
    service_id: Mapped[StrUUID | None] = mapped_column(
        ForeignKey("service.service_id", ondelete="SET NULL"), index=True
    )
    ticket_id: Mapped[StrUUID | None] = mapped_column(
        ForeignKey("ticket.ticket_id", ondelete="SET NULL"), index=True
    )
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
    pteam_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("pteam.pteam_id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("account.user_id", ondelete="CASCADE"), index=True
    )
    expiration: Mapped[datetime]
    limit_count: Mapped[int | None]  # None for unlimited
    used_count: Mapped[int] = mapped_column(server_default="0")

    pteam = relationship("PTeam", back_populates="invitations")
    inviter = relationship("Account", back_populates="pteam_invitations")

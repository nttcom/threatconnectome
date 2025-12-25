import enum
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    ForeignKey,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    case,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry, relationship
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


class PackageType(str, enum.Enum):
    LANG = "lang"
    OS = "os"
    PACKAGE = "package"


class TicketHandlingStatusType(str, enum.Enum):
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


class ImpactCategoryEnum(str, enum.Enum):
    # https://attack.mitre.org/tactics/TA0105/
    DAMAGE_TO_PROPERTY = "damage_to_property"
    DENIAL_OF_CONTROL = "denial_of_control"
    DENIAL_OF_VIEW = "denial_of_view"
    LOSS_OF_AVAILABILITY = "loss_of_availability"
    LOSS_OF_CONTROL = "loss_of_control"
    LOSS_OF_PRODUCTIVITY_AND_REVENUE = "loss_of_productivity_and_revenue"
    LOSS_OF_PROTECTION = "loss_of_protection"
    LOSS_OF_SAFETY = "loss_of_safety"
    LOSS_OF_VIEW = "loss_of_view"
    MANIPULATION_OF_CONTROL = "manipulation_of_control"
    MANIPULATION_OF_VIEW = "manipulation_of_view"
    THEFT_OF_OPERATIONAL_INFORMATION = "theft_of_operational_information"


class ObjectCategoryEnum(str, enum.Enum):
    SERVER = "server"
    CLIENT_DEVICE = "client_device"
    MOBILE_DEVICE = "mobile_device"
    NETWORK_DEVICE = "network_device"
    STORAGE = "storage"
    IOT_DEVICE = "iot_device"
    PHYSICAL_MEDIA = "physical_media"
    FACILITY = "facility"
    PERSON = "person"


class ProductCategoryEnum(str, enum.Enum):
    OS = "OS"
    RUNTIME = "RUNTIME"
    MIDDLEWARE = "MIDDLEWARE"
    PACKAGE = "PACKAGE"


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
            list[str]: ARRAY(Text),
            list[StrUUID]: ARRAY(String(36)),
            list[Str255]: ARRAY(String(255)),
            bytes: LargeBinary(),
        }
    )


# primary tables #


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


class Account(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.user_id:
            self.user_id = str(uuid.uuid4())

    __tablename__ = "account"

    user_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(unique=True)
    email: Mapped[Str255]
    disabled: Mapped[bool] = mapped_column(default=False)
    years: Mapped[int]

    pteam_invitations = relationship("PTeamInvitation", back_populates="inviter")
    action_logs = relationship("ActionLog", back_populates="executed_by")
    pteam_roles = relationship(
        "PTeamAccountRole", back_populates="account", cascade="all, delete-orphan"
    )
    account_default_pteam = relationship(
        "AccountDefaultPTeam",
        cascade="all, delete-orphan",
        uselist=False,
    )


class AccountDefaultPTeam(Base):
    __tablename__ = "accountdefaultpteam"

    user_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("account.user_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    default_pteam_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("pteam.pteam_id", ondelete="CASCADE"), index=True
    )


class PackageVersion(Base):
    __tablename__ = "packageversion"
    __table_args__ = (
        UniqueConstraint("package_id", "version", name="package_version_package_id_version_key"),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.package_version_id:
            self.package_version_id = str(uuid.uuid4())

    package_version_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column()
    package_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("package.package_id", ondelete="CASCADE"), index=True
    )

    package = relationship("Package", back_populates="package_versions")
    dependencies = relationship(
        "Dependency", back_populates="package_version", cascade="all, delete-orphan"
    )


class Package(Base):
    __tablename__ = "package"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.package_id:
            self.package_id = str(uuid.uuid4())

    @hybrid_property
    def vuln_matching_ecosystem(self) -> str:
        """
        Returns the ecosystem string for vulnerability matching.
        If the ecosystem starts with "alpine-",
        it change the value to include only the minor version.
        If it starts with "rocky-", it keeps only the major version.
        Example: "alpine-3.22.0" → "alpine-3.22", "rocky-9.3" → "rocky-9"
        For other ecosystems, returns the original value.
        """
        if not self.ecosystem:
            return self.ecosystem
        if self.ecosystem.startswith("alpine-"):
            parts = self.ecosystem.split("-")
            if len(parts) == 2:
                version = parts[1].split(".")
                if len(version) >= 2:
                    return f"alpine-{version[0]}.{version[1]}"
        elif self.ecosystem.startswith("rocky-"):
            parts = self.ecosystem.split("-")
            if len(parts) == 2:
                version = parts[1].split(".")
                if len(version) >= 1:
                    return f"rocky-{version[0]}"
        return self.ecosystem

    @vuln_matching_ecosystem.inplace.expression
    def vuln_matching_ecosystem_for_sql_query(cls):
        """
        SQL expression for vuln_matching_ecosystem.
        If the ecosystem starts with 'alpine-', returns only up to the minor version
        (e.g., 'alpine-3.22.0' → 'alpine-3.22').
        If the ecosystem starts with 'rocky-', returns only the major version
        (e.g., 'rocky-9.3' → 'rocky-9').
        Otherwise, returns the original ecosystem value.
        """
        return case(
            (
                # Beginning with "alpine-", split in two by "-", split in three by "."
                cls.ecosystem.like("alpine-%")
                & (func.array_length(func.string_to_array(cls.ecosystem, "-"), 1) == 2)
                & (
                    func.array_length(
                        func.string_to_array(func.split_part(cls.ecosystem, "-", 2), "."), 1
                    )
                    == 3
                ),
                func.concat(
                    "alpine-",
                    func.split_part(func.split_part(cls.ecosystem, "-", 2), ".", 1),
                    ".",
                    func.split_part(func.split_part(cls.ecosystem, "-", 2), ".", 2),
                ),
            ),
            (
                # rocky-: "rocky-x.y" → "rocky-x"
                cls.ecosystem.like("rocky-%")
                & (func.array_length(func.string_to_array(cls.ecosystem, "-"), 1) == 2)
                & (
                    func.array_length(
                        func.string_to_array(func.split_part(cls.ecosystem, "-", 2), "."), 1
                    )
                    > 1
                ),
                func.concat(
                    "rocky-",
                    func.split_part(func.split_part(cls.ecosystem, "-", 2), ".", 1),
                ),
            ),
            else_=cls.ecosystem,
        )

    package_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    ecosystem: Mapped[str] = mapped_column()

    type: Mapped[PackageType] = mapped_column()

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": PackageType.PACKAGE,
    }

    package_versions = relationship(
        "PackageVersion", back_populates="package", cascade="all, delete-orphan"
    )


class LangPackage(Package):
    __mapper_args__ = {
        "polymorphic_identity": PackageType.LANG,
    }


class OSPackage(Package):
    source_name: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": PackageType.OS,
    }


UniqueConstraint(
    Package.name,
    Package.ecosystem,
    OSPackage.source_name,
    name="package_name_ecosystem_source_name_key",
    postgresql_nulls_not_distinct=True,
)


class Dependency(Base):
    __tablename__ = "dependency"
    __table_args__: tuple = (
        UniqueConstraint(
            "service_id",
            "package_version_id",
            "target",
            name="dependency_service_id_package_version_id_target_key",
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
    package_version_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("packageversion.package_version_id", ondelete="CASCADE"), index=True
    )
    target: Mapped[str]
    package_manager: Mapped[str]
    dependency_mission_impact: Mapped[MissionImpactEnum | None] = mapped_column(
        server_default=None, nullable=True
    )

    service = relationship("Service", back_populates="dependencies")
    package_version = relationship(
        "PackageVersion", uselist=False, back_populates="dependencies", lazy="joined"
    )
    tickets = relationship("Ticket", back_populates="dependency", cascade="all, delete-orphan")
    package_eol_dependencies = relationship(
        "PackageEoLDependency", back_populates="dependency", cascade="all, delete-orphan"
    )


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
    sbom_uploaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    description: Mapped[str | None]
    keywords: Mapped[list[Str255]] = mapped_column(server_default="{}")

    pteam = relationship("PTeam", back_populates="services")
    dependencies = relationship(
        "Dependency", back_populates="service", cascade="all, delete-orphan"
    )
    thumbnail = relationship("ServiceThumbnail", uselist=False, cascade="all, delete-orphan")
    ecosystem_eol_dependencies = relationship(
        "EcosystemEoLDependency", back_populates="service", cascade="all, delete-orphan"
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
        UniqueConstraint(
            "package_version_id", "vuln_id", name="threat_package_version_id_vuln_id_key"
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.threat_id:
            self.threat_id = str(uuid.uuid4())

    threat_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    package_version_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("packageversion.package_version_id", ondelete="CASCADE"), index=True
    )
    vuln_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("vuln.vuln_id", ondelete="CASCADE"), index=True
    )

    vuln = relationship("Vuln", back_populates="threats")
    package_version = relationship("PackageVersion")
    tickets = relationship("Ticket", back_populates="threat", cascade="all, delete-orphan")


class Ticket(Base):
    __tablename__ = "ticket"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.ticket_id:
            self.ticket_id = str(uuid.uuid4())

    ticket_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    threat_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("threat.threat_id", ondelete="CASCADE"), index=True
    )
    dependency_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("dependency.dependency_id", ondelete="CASCADE"), index=True
    )
    ticket_safety_impact: Mapped[SafetyImpactEnum | None] = mapped_column(nullable=True)
    ticket_safety_impact_change_reason: Mapped[str | None] = mapped_column(nullable=True)
    ssvc_deployer_priority: Mapped[SSVCDeployerPriorityEnum | None] = mapped_column(nullable=True)

    dependency = relationship("Dependency", back_populates="tickets")
    threat = relationship("Threat", uselist=False, back_populates="tickets")
    alerts = relationship("Alert", back_populates="ticket")
    ticket_status = relationship("TicketStatus", uselist=False, cascade="all, delete-orphan")
    insight = relationship(
        "Insight", uselist=False, back_populates="ticket", cascade="all, delete-orphan"
    )


class TicketStatus(Base):
    __tablename__ = "ticketstatus"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.status_id:
            self.status_id = str(uuid.uuid4())

    status_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    ticket_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("ticket.ticket_id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[StrUUID | None] = mapped_column(
        ForeignKey("account.user_id", ondelete="SET NULL"), index=True
    )
    ticket_handling_status: Mapped[TicketHandlingStatusType]
    note: Mapped[str | None]
    logging_ids: Mapped[list[StrUUID]] = mapped_column(default=[])
    assignees: Mapped[list[StrUUID]] = mapped_column(default=[])
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=current_timestamp()
    )

    action_logs = relationship(
        "ActionLog",
        primaryjoin="TicketStatus.logging_ids.any(foreign(ActionLog.logging_id))",
        collection_class=set,
        viewonly=True,
    )


class Alert(Base):
    __tablename__ = "alert"

    def __init__(self, *args, **kwargs) -> None:
        now = datetime.now(timezone.utc)
        super().__init__(*args, **kwargs)
        if not self.alert_id:
            self.alert_id = str(uuid.uuid4())
        if not self.alerted_at:
            self.alerted_at = now

    alert_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    ticket_id: Mapped[StrUUID | None] = mapped_column(
        ForeignKey("ticket.ticket_id", ondelete="SET NULL"), index=True, nullable=True
    )
    alerted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=current_timestamp()
    )
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


class Vuln(Base):
    __tablename__ = "vuln"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.vuln_id:
            self.vuln_id = str(uuid.uuid4())
        if not self.exploitation:
            self.exploitation = ExploitationEnum.NONE
        if not self.automatable:
            self.automatable = AutomatableEnum.NO

    vuln_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    cve_id: Mapped[str | None] = mapped_column(nullable=True)
    detail: Mapped[str]
    title: Mapped[Str255]
    created_by: Mapped[StrUUID | None] = mapped_column(
        ForeignKey("account.user_id", ondelete="SET NULL"), index=True, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=current_timestamp()
    )
    exploitation: Mapped[ExploitationEnum] = mapped_column(server_default=ExploitationEnum.NONE)
    automatable: Mapped[AutomatableEnum] = mapped_column(server_default=AutomatableEnum.NO)
    cvss_v3_score: Mapped[float | None] = mapped_column(server_default=None, nullable=True)

    affects = relationship("Affect", back_populates="vuln", cascade="all, delete-orphan")
    threats = relationship("Threat", back_populates="vuln", cascade="all, delete-orphan")


class Affect(Base):
    __tablename__ = "affect"
    __table_args__ = (
        UniqueConstraint(
            "vuln_id",
            "affected_name",
            "ecosystem",
            name="affect_vuln_id_affected_name_ecosystem_key",
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.affect_id:
            self.affect_id = str(uuid.uuid4())

    affect_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    vuln_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("vuln.vuln_id", ondelete="CASCADE"), index=True
    )

    affected_versions: Mapped[list[str]] = mapped_column(default=[])
    fixed_versions: Mapped[list[str]] = mapped_column(default=[])
    affected_name: Mapped[str] = mapped_column()
    ecosystem: Mapped[str] = mapped_column()

    vuln = relationship("Vuln", back_populates="affects")


class ActionLog(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.logging_id:
            self.logging_id = str(uuid.uuid4())

    __tablename__ = "actionlog"

    logging_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    vuln_id: Mapped[StrUUID]  # snapshot: don't set ForeignKey.
    action: Mapped[str]  # snapshot: don't update
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
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=current_timestamp()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=current_timestamp()
    )

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
    expiration: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    limit_count: Mapped[int | None]  # None for unlimited
    used_count: Mapped[int] = mapped_column(server_default="0")

    pteam = relationship("PTeam", back_populates="invitations")
    inviter = relationship("Account", back_populates="pteam_invitations")


class Insight(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.insight_id:
            self.insight_id = str(uuid.uuid4())

    __tablename__ = "insight"

    insight_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    ticket_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("ticket.ticket_id", ondelete="CASCADE"), index=True, unique=True
    )
    description: Mapped[str]
    data_processing_strategy: Mapped[str]

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=current_timestamp()
    )

    ticket = relationship("Ticket", back_populates="insight")
    threat_scenarios = relationship(
        "ThreatScenario", back_populates="insight", cascade="all, delete-orphan"
    )
    affected_objects = relationship(
        "AffectedObject", back_populates="insight", cascade="all, delete-orphan"
    )
    insight_references = relationship(
        "InsightReference", back_populates="insight", cascade="all, delete-orphan"
    )


class ThreatScenario(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.threat_scenario_id:
            self.threat_scenario_id = str(uuid.uuid4())

    __tablename__ = "threatscenario"

    threat_scenario_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    insight_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("insight.insight_id", ondelete="CASCADE"), index=True
    )
    impact_category: Mapped[ImpactCategoryEnum]
    title: Mapped[Str255]
    description: Mapped[str]

    insight = relationship("Insight", back_populates="threat_scenarios")


class AffectedObject(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.object_id:
            self.object_id = str(uuid.uuid4())

    __tablename__ = "affectedobject"

    object_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    insight_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("insight.insight_id", ondelete="CASCADE"), index=True
    )
    object_category: Mapped[ObjectCategoryEnum]
    name: Mapped[Str255]
    description: Mapped[str]

    insight = relationship("Insight", back_populates="affected_objects")


class InsightReference(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.insight_reference_id:
            self.insight_reference_id = str(uuid.uuid4())

    __tablename__ = "insightreference"

    insight_reference_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    insight_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("insight.insight_id", ondelete="CASCADE"), index=True
    )
    link_text: Mapped[Str255]
    url: Mapped[Str255 | None]

    insight = relationship("Insight", back_populates="insight_references")


class EoLProduct(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.eol_product_id:
            self.eol_product_id = str(uuid.uuid4())

    __tablename__ = "eolproduct"

    eol_product_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    name: Mapped[Str255]
    product_category: Mapped[ProductCategoryEnum]
    description: Mapped[str | None]
    is_ecosystem: Mapped[bool] = mapped_column(default=False)
    matching_product_name: Mapped[Str255]

    eol_versions = relationship(
        "EoLVersion", back_populates="eol_product", cascade="all, delete-orphan"
    )


class EoLVersion(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.eol_version_id:
            self.eol_version_id = str(uuid.uuid4())

    __tablename__ = "eolversion"

    eol_version_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    eol_product_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("eolproduct.eol_product_id", ondelete="CASCADE"), index=True
    )
    version: Mapped[Str255]
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    eol_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    matching_version: Mapped[Str255]

    eol_product = relationship("EoLProduct", back_populates="eol_versions")
    package_eol_dependencies = relationship(
        "PackageEoLDependency", back_populates="eol_version", cascade="all, delete-orphan"
    )
    ecosystem_eol_dependencies = relationship(
        "EcosystemEoLDependency", back_populates="eol_version", cascade="all, delete-orphan"
    )


class PackageEoLDependency(Base):
    __tablename__ = "packageeoldependency"
    __table_args__ = (
        UniqueConstraint(
            "dependency_id",
            "eol_version_id",
            name="packageeoldependency_dependency_id_eol_version_id_key",
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.package_eol_dependency_id:
            self.package_eol_dependency_id = str(uuid.uuid4())

    package_eol_dependency_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    dependency_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("dependency.dependency_id", ondelete="CASCADE"), index=True
    )
    eol_version_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("eolversion.eol_version_id", ondelete="CASCADE"), index=True
    )
    eol_notification_sent: Mapped[bool] = mapped_column(default=False)

    dependency = relationship("Dependency", back_populates="package_eol_dependencies")
    eol_version = relationship("EoLVersion", back_populates="package_eol_dependencies")


class EcosystemEoLDependency(Base):
    __tablename__ = "ecosystemeoldependency"
    __table_args__ = (
        UniqueConstraint(
            "service_id",
            "eol_version_id",
            name="ecosystemeoldependency_service_id_eol_version_id_key",
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.ecosystem_eol_dependency_id:
            self.ecosystem_eol_dependency_id = str(uuid.uuid4())

    ecosystem_eol_dependency_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    service_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("service.service_id", ondelete="CASCADE"), index=True
    )
    eol_version_id: Mapped[StrUUID] = mapped_column(
        ForeignKey("eolversion.eol_version_id", ondelete="CASCADE"), index=True
    )
    eol_notification_sent: Mapped[bool] = mapped_column(default=False)

    service = relationship("Service", back_populates="ecosystem_eol_dependencies")
    eol_version = relationship("EoLVersion", back_populates="ecosystem_eol_dependencies")

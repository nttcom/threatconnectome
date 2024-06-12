import json
from datetime import datetime
from hashlib import md5
from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.alert import send_alert_to_pteam
from app.constants import MEMBER_UUID, NOT_MEMBER_UUID, SYSTEM_UUID
from app.ssvc import calculate_ssvc_deployer_priority
from app.version import (
    PackageFamily,
    VulnerableRange,
    gen_version_instance,
)


def check_pteam_membership(
    db: Session,
    pteam: models.PTeam | None,
    user: models.Account | None,
    ignore_ateam: bool = False,
) -> bool:
    if not pteam or not user:
        return False
    if user.user_id == str(SYSTEM_UUID):
        return True
    if user in pteam.members:
        return True
    if ignore_ateam:
        return False
    # check if a member of ateam which watches the pteam
    if any(user in ateam.members for ateam in pteam.ateams):
        return True
    return False


def check_pteam_auth(
    db: Session,
    pteam: models.PTeam,
    user: models.Account,
    required: models.PTeamAuthIntFlag,
) -> bool:
    if user.user_id == str(SYSTEM_UUID):
        return True

    user_auth = persistence.get_pteam_authority(db, pteam.pteam_id, user.user_id)
    int_auth = int(user_auth.authority) if user_auth else 0
    # append auth via pseudo-users
    if not_member_auth := persistence.get_pteam_authority(db, pteam.pteam_id, NOT_MEMBER_UUID):
        int_auth |= not_member_auth.authority
    if user in pteam.members and (
        member_auth := persistence.get_pteam_authority(db, pteam.pteam_id, MEMBER_UUID)
    ):
        int_auth |= member_auth.authority

    return int_auth & required == required


def check_ateam_membership(
    ateam: models.ATeam | None,
    user: models.Account | None,
) -> bool:
    if not ateam or not user:
        return False
    if user.user_id == str(SYSTEM_UUID):
        return True
    if user in ateam.members:
        return True
    return False


def check_ateam_auth(
    db: Session,
    ateam: models.ATeam,
    user: models.Account,
    required: models.ATeamAuthIntFlag,
) -> bool:
    if user.user_id == str(SYSTEM_UUID):
        return True

    user_auth = persistence.get_ateam_authority(db, ateam.ateam_id, user.user_id)
    int_auth = int(user_auth.authority) if user_auth else 0
    # append auth via pseudo-users
    if not_member_auth := persistence.get_ateam_authority(db, ateam.ateam_id, NOT_MEMBER_UUID):
        int_auth |= not_member_auth.authority
    if user in ateam.members and (
        member_auth := persistence.get_ateam_authority(db, ateam.ateam_id, MEMBER_UUID)
    ):
        int_auth |= member_auth.authority

    return int_auth & required == required


def get_tag_ids_with_parent_ids(tags: Sequence[models.Tag]) -> Sequence[str]:
    tag_ids_set: set[str] = set()
    for tag in tags:
        tag_ids_set.add(tag.tag_id)
        if tag.parent_id and tag.parent_id != tag.tag_id:
            tag_ids_set.add(tag.parent_id)
    return list(tag_ids_set)


def get_sorted_topics(topics: Sequence[models.Topic]) -> Sequence[models.Topic]:
    """
    Sort topics with standard sort rules -- (threat_impact ASC, updated_at DESC)
    """
    return sorted(
        topics,
        key=lambda topic: (
            topic.threat_impact,
            -(dt.timestamp() if (dt := topic.updated_at) else 0),
        ),
    )


def _pick_parent_tag(tag_name: str) -> str | None:
    if len(tag_name.split(":", 2)) == 3:  # supported format
        return tag_name.rsplit(":", 1)[0] + ":"  # trim the right most field
    return None


def check_topic_action_tags_integrity(
    topic_tags: Sequence[str] | Sequence[models.Tag],  # tag_name list or topic.tags
    action_tags: Sequence[str] | None,  # action.ext.get("tags")
) -> bool:
    if not action_tags:
        return True

    topic_tag_strs = {x if isinstance(x, str) else x.tag_name for x in topic_tags}
    for action_tag in action_tags:
        if action_tag not in topic_tag_strs and _pick_parent_tag(action_tag) not in topic_tag_strs:
            return False
    return True


def get_or_create_misp_tag(db: Session, tag_name: str) -> models.MispTag:
    if misp_tag := persistence.get_misp_tag_by_name(db, tag_name):
        return misp_tag

    misp_tag = models.MispTag(tag_name=tag_name)
    persistence.create_misp_tag(db, misp_tag)
    return misp_tag


def get_or_create_topic_tag(db: Session, tag_name: str) -> models.Tag:
    if tag := persistence.get_tag_by_name(db, tag_name):  # already exists
        return tag

    tag = models.Tag(tag_name=tag_name, parent_id=None, parent_name=None)
    if not (parent_name := _pick_parent_tag(tag_name)):  # no parent: e.g. "tag1"
        persistence.create_tag(db, tag)
        return tag

    if parent_name == tag_name:  # parent is myself
        tag.parent_id = tag.tag_id
        tag.parent_name = tag_name
    else:
        parent = get_or_create_topic_tag(db, parent_name)
        tag.parent_id = parent.tag_id
        tag.parent_name = parent.tag_name

    persistence.create_tag(db, tag)

    return tag


def calculate_topic_content_fingerprint(
    title: str,
    abstract: str,
    threat_impact: int,
    tag_names: Sequence[str],
) -> str:
    data = {
        "title": title,
        "abstract": abstract,
        "threat_impact": threat_impact,
        "tag_names": sorted(set(tag_names)),
    }
    return md5(json.dumps(data, sort_keys=True).encode()).hexdigest()


def get_pteam_ext_tags(db: Session, pteam: models.PTeam) -> Sequence[schemas.ExtTagResponse]:
    ext_tags_dict: dict[str, schemas.ExtTagResponse] = {}
    for service in pteam.services:
        for dependency in service.dependencies:
            ext_tag = ext_tags_dict.get(
                dependency.tag_id,
                schemas.ExtTagResponse(
                    tag_id=dependency.tag_id,
                    tag_name=dependency.tag.tag_name,
                    parent_id=dependency.tag.parent_id,
                    parent_name=dependency.tag.parent_name,
                    references=[],
                ),
            )
            ext_tag.references.append(
                {
                    "service": service.service_name,
                    "target": dependency.target,
                    "version": dependency.version,
                }
            )
            ext_tags_dict[dependency.tag_id] = ext_tag

    return sorted(ext_tags_dict.values(), key=lambda x: x.tag_name)


def set_pteam_topic_status_internal(
    db: Session,
    current_user: models.Account,
    pteam: models.PTeam,
    topic: models.Topic,
    tag: models.Tag,  # should be PTeamTag, not TopicTag
    data: schemas.TopicStatusRequest,
) -> schemas.PTeamTopicStatusResponse | None:
    current_status = persistence.get_current_pteam_topic_tag_status(
        db, pteam.pteam_id, topic.topic_id, tag.tag_id
    )
    if (
        (not current_status or current_status.topic_status == models.TopicStatusType.alerted)
        and data.topic_status == models.TopicStatusType.acknowledged
        and not data.assignees  # first ack without assignees
    ):
        assignees = [current_user.user_id]  # force assign current_user
    else:
        assignees = list(map(str, data.assignees))
    new_status = models.PTeamTopicTagStatus(
        pteam_id=pteam.pteam_id,
        topic_id=topic.topic_id,
        tag_id=tag.tag_id,
        topic_status=data.topic_status,
        user_id=current_user.user_id,
        note=data.note,
        logging_ids=list(map(str, set(data.logging_ids))),
        assignees=list(set(assignees)),
        scheduled_at=data.scheduled_at,
        created_at=datetime.now(),
    )
    persistence.create_pteam_topic_tag_status(db, new_status)

    if not current_status:
        current_status = models.CurrentPTeamTopicTagStatus(
            pteam_id=pteam.pteam_id,
            topic_id=topic.topic_id,
            tag_id=tag.tag_id,
            status_id=None,  # fill later
            topic_status=None,  # fill later
            threat_impact=None,  # fill later
            updated_at=None,  # fill later
        )
        persistence.create_current_pteam_topic_tag_status(db, current_status)

    current_status.status_id = new_status.status_id
    current_status.topic_status = new_status.topic_status
    current_status.threat_impact = topic.threat_impact
    current_status.updated_at = (
        None if new_status.topic_status == models.TopicStatusType.completed else topic.updated_at
    )
    db.flush()

    return command.pteam_topic_tag_status_to_response(db, new_status)


def _pick_vulnerable_version_strings_from_actions(
    actions: Sequence[models.TopicAction],
    tag: models.Tag,
) -> set[str]:
    tag_name = tag.tag_name
    parent_name = tag.parent_name
    vulnerable_versions = set()
    for action in actions:
        vulnerable_versions |= set(action.ext.get("vulnerable_versions", {}).get(tag_name, []))
        if parent_name and parent_name != tag_name:
            vulnerable_versions |= set(
                action.ext.get("vulnerable_versions", {}).get(parent_name, [])
            )
    result: set[str] = set()
    for vulnerable_version in vulnerable_versions:
        result |= set(vulnerable_version.split("||"))
    return result


def _complete_topic(
    db: Session,
    pteam: models.PTeam,
    tag: models.Tag,
    actions: Sequence[models.TopicAction],
):
    if not actions:
        return

    topic = actions[0].topic
    system_account = persistence.get_system_account(db)
    now = datetime.now()

    logging_ids = []
    for action in actions:
        action_log = models.ActionLog(
            action_id=action.action_id,
            topic_id=topic.topic_id,
            action=action.action,
            action_type=action.action_type,
            recommended=action.recommended,
            user_id=system_account.user_id,
            pteam_id=pteam.pteam_id,
            email=system_account.email,
            executed_at=now,
            created_at=now,
        )
        persistence.create_action_log(db, action_log)
        logging_ids.append(action_log.logging_id)

    topicStatusRequest = schemas.TopicStatusRequest(
        topic_status=models.TopicStatusType.completed,
        logging_ids=list(map(UUID, logging_ids)),
        note="auto closed by system",
    )
    set_pteam_topic_status_internal(
        db,
        system_account,
        pteam,
        topic,
        tag,
        topicStatusRequest,
    )


def pteamtag_try_auto_close_topic(
    db: Session,
    pteam: models.PTeam,
    tag: models.Tag,  # should be bound to pteam, not to topic
    topic: models.Topic,
):
    try:
        # pick unique reference versions to compare. (omit empty -- maybe added on WebUI)
        reference_versions = {
            dependency.version
            for service in pteam.services
            for dependency in service.dependencies
            if dependency.tag == tag and dependency.version
        }
        if not reference_versions:
            return  # no references to compare
        # pick all actions which matched on tags
        actions = command.pick_actions_related_to_pteam_tag_from_topic(db, topic, pteam, tag)
        if not actions:  # this topic does not have actions for this pteamtag
            return
        # pick all matched vulnerables from actions
        vulnerable_strings = _pick_vulnerable_version_strings_from_actions(actions, tag)
        if not vulnerable_strings:
            return

        package_family = PackageFamily.from_tag_name(tag.tag_name)
        vulnerables = {
            VulnerableRange.from_string(package_family, vulnerable_string)
            for vulnerable_string in vulnerable_strings
        }
        references = {
            gen_version_instance(package_family, reference_version)
            for reference_version in reference_versions
        }
        # detect vulnerable
        if any(vulnerable.detect_matched(references) for vulnerable in vulnerables):
            return  # found at least 1 vulnerable
    except ValueError:  # found invalid, ambiguous or uncomparable
        return  # human check required

    # This topic has actionable actions, but no actions left to carry out for this pteamtag.
    _complete_topic(db, pteam, tag, actions)


def auto_close_by_pteamtags(db: Session, pteamtags: Sequence[tuple[models.PTeam, models.Tag]]):
    for pteam, tag in pteamtags:
        for topic in command.pick_topics_related_to_pteam_tag(db, pteam, tag):
            pteamtag_try_auto_close_topic(db, pteam, tag, topic)


def auto_close_by_topic(db: Session, topic: models.Topic):
    for pteam, tag in command.pick_pteam_tags_related_to_topic(db, topic):
        pteamtag_try_auto_close_topic(db, pteam, tag, topic)


def threat_meets_condition_to_create_ticket(db: Session, threat: models.Threat) -> bool:
    if not (actions := persistence.get_actions_by_topic_id(db, threat.topic_id)):
        return False
    tag = threat.dependency.tag
    action_tag_names_set: set = set()

    for action in actions:
        action_tag_names = action.ext.get("tags")
        if action_tag_names is None:
            continue
        action_tag_names_set |= set(action_tag_names)

    for action_tag_name in action_tag_names_set:
        tag_by_action = persistence.get_tag_by_name(db, action_tag_name)
        if (
            threat.topic
            and tag_by_action
            and (tag_by_action.tag_id == tag.tag_id or tag_by_action.tag_id == tag.parent_id)
        ):
            return True
    return False


def ticket_meets_condition_to_create_alert(ticket: models.Ticket) -> bool:
    # abort if deployer_priofiry is not yet calclated
    if ticket.ssvc_deployer_priority is None:
        return False
    if not (
        int_priority := {
            models.SSVCDeployerPriorityEnum.IMMEDIATE: 1,
            models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE: 2,
            models.SSVCDeployerPriorityEnum.SCHEDULED: 3,
            models.SSVCDeployerPriorityEnum.DEFER: 4,
        }.get(ticket.ssvc_deployer_priority)
    ):
        raise ValueError(f"Invalid SSVCDeployerPriority: {ticket.ssvc_deployer_priority}")

    # WORKAROUND
    # use pteam.alert_threat_impact as threshold for alert.
    # threshold should be defined in pteam and/or service.
    pteam = ticket.threat.dependency.service.pteam
    int_threshold = pteam.alert_threat_impact or 4
    return int_priority <= int_threshold


def count_service_solved_tickets_per_threat_impact(
    service: models.Service,
    tag_id: UUID | str,
) -> dict[str, int]:
    _completed = models.TopicStatusType.completed
    threat_counts_rows: dict[str, int] = {"1": 0, "2": 0, "3": 0, "4": 0}
    prev_topic_id: set = set()

    for dependency in service.dependencies:
        if dependency.tag_id != str(tag_id):
            continue
        for threat in dependency.threats:
            if not threat.ticket:
                continue

            _curent_ticket = threat.ticket.current_ticket_status
            if _curent_ticket.topic_status == _completed and threat.topic_id not in prev_topic_id:
                threat_imapct_str = str(_curent_ticket.threat_impact)
                threat_counts_rows[threat_imapct_str] += 1
                prev_topic_id.add(threat.topic_id)

    return threat_counts_rows


def count_service_unsolved_tickets_per_threat_impact(
    service: models.Service,
    tag_id: UUID | str,
) -> dict[str, int]:
    _completed = models.TopicStatusType.completed
    threat_counts_rows: dict[str, int] = {"1": 0, "2": 0, "3": 0, "4": 0}
    prev_topic_id: set = set()

    for dependency in service.dependencies:
        if dependency.tag_id != str(tag_id):
            continue
        for threat in dependency.threats:
            if not threat.ticket:
                continue

            _curent_ticket = threat.ticket.current_ticket_status
            if _curent_ticket.topic_status != _completed and threat.topic_id not in prev_topic_id:
                threat_imapct_str = str(_curent_ticket.threat_impact)
                threat_counts_rows[threat_imapct_str] += 1
                prev_topic_id.add(threat.topic_id)

    return threat_counts_rows


def get_sorted_solved_ticket_ids_by_service_tag_and_status(
    service: models.Service,
    tag_id: UUID | str,
) -> list[dict]:
    _completed = models.TopicStatusType.completed
    topic_ticket_ids: list[dict] = []
    topic_ticket_ids_dict: dict = {}

    for dependency in service.dependencies:
        if dependency.tag_id != str(tag_id):
            continue
        for threat in dependency.threats:
            if not threat.ticket:
                continue

            _curent_ticket = threat.ticket.current_ticket_status
            if _curent_ticket.topic_status == _completed:
                topic_ticket_ids.append(
                    {"topic_id": threat.topic_id, "ticket_id": _curent_ticket.ticket_id}
                )

    for _topic_ticket_id in topic_ticket_ids:
        if _topic_ticket_id["topic_id"] not in topic_ticket_ids_dict:
            topic_ticket_ids_dict[_topic_ticket_id["topic_id"]] = {
                "topic_id": _topic_ticket_id["topic_id"],
                "ticket_ids": [],
            }
        topic_ticket_ids_dict[_topic_ticket_id["topic_id"]]["ticket_ids"].append(
            _topic_ticket_id["ticket_id"]
        )

    result = list(topic_ticket_ids_dict.values())

    return result


def get_sorted_unsolved_ticket_ids_by_service_tag_and_status(
    service: models.Service,
    tag_id: UUID | str,
) -> list[dict]:
    _completed = models.TopicStatusType.completed
    topic_ticket_ids: list[dict] = []
    topic_ticket_ids_dict: dict = {}

    for dependency in service.dependencies:
        if dependency.tag_id != str(tag_id):
            continue
        for threat in dependency.threats:
            if not threat.ticket:
                continue

            _curent_ticket = threat.ticket.current_ticket_status
            if _curent_ticket.topic_status != _completed:
                topic_ticket_ids.append(
                    {"topic_id": threat.topic_id, "ticket_id": _curent_ticket.ticket_id}
                )

    for _topic_ticket_id in topic_ticket_ids:
        if _topic_ticket_id["topic_id"] not in topic_ticket_ids_dict:
            topic_ticket_ids_dict[_topic_ticket_id["topic_id"]] = {
                "topic_id": _topic_ticket_id["topic_id"],
                "ticket_ids": [],
            }
        topic_ticket_ids_dict[_topic_ticket_id["topic_id"]]["ticket_ids"].append(
            _topic_ticket_id["ticket_id"]
        )

    result = list(topic_ticket_ids_dict.values())

    return result


def create_ticket_internal(
    db: Session,
    threat: models.Threat,
    now: datetime | None = None,
) -> models.Ticket:
    if now is None:
        now = datetime.now()

    ticket = models.Ticket(
        threat_id=threat.threat_id,
        created_at=now,
        updated_at=now,
        ssvc_deployer_priority=calculate_ssvc_deployer_priority(threat),
    )
    persistence.create_ticket(db, ticket)

    # create CurrentTicketStatus without TicketStatus
    current_status = models.CurrentTicketStatus(
        ticket_id=ticket.ticket_id,
        status_id=None,
        topic_status=models.TopicStatusType.alerted,
        threat_impact=threat.topic.threat_impact,
        updated_at=threat.topic.updated_at,
    )
    persistence.create_current_ticket_status(db, current_status)

    # send alert if needed
    if ticket_meets_condition_to_create_alert(ticket):
        alert = models.Alert(
            ticket_id=ticket.ticket_id,
            alerted_at=now,
            alert_content=threat.topic.hint_for_action,
        )
        persistence.create_alert(db, alert)
        send_alert_to_pteam(alert)

    return ticket


def fix_threats_for_topic(db: Session, topic: models.Topic):
    now = datetime.now()

    # remove threats which lost related dependency -- for the case Topic.tags updated
    valid_dependency_ids = {dependency.dependency_id for dependency in topic.dependencies_via_tag}
    for threat in topic.threats:
        if threat.dependency_id not in valid_dependency_ids:
            persistence.delete_threat(db, threat)

    # collect VulnerableRanges for each tags from TopicAction
    vulnerable_range_strings_dict: dict[str, set[str]] = {}  # tag_name: range strings
    for action in topic.actions:
        if not action.ext or not (vulnerable_versions := action.ext.get("vulnerable_versions")):
            continue
        for tag_name, vulnerable_range_strings in vulnerable_versions.items():
            if (tmp_str_set := vulnerable_range_strings_dict.get(tag_name)) is None:
                tmp_str_set = set()
                vulnerable_range_strings_dict[tag_name] = tmp_str_set
            for vulnerable_range_string in vulnerable_range_strings:
                tmp_str_set |= set(vulnerable_range_string.split("||"))
    vulnerables_dict: dict[str, set[VulnerableRange]] = {}  # tag_name: VulnerableRanges
    for tag_name, vulnerable_range_strings in vulnerable_range_strings_dict.items():
        package_family = PackageFamily.from_tag_name(tag_name)
        if (tmp_obj_set := vulnerables_dict.get(tag_name)) is None:
            tmp_obj_set = set()
            vulnerables_dict[tag_name] = tmp_obj_set
        for vulnerable_range_string in vulnerable_range_strings:
            try:
                tmp_obj_set.add(
                    VulnerableRange.from_string(package_family, vulnerable_range_string)
                )
            except ValueError:
                pass  # ignore unexpected range strings

    # check and fix for each dependencies related to the topic
    for dependency in topic.dependencies_via_tag:
        tag = dependency.tag
        try:
            dependency_version = gen_version_instance(
                PackageFamily.from_tag_name(tag.tag_name), dependency.version
            )
        except ValueError:
            dependency_version = None

        tmp_threats = persistence.search_threats(db, dependency.dependency_id, topic.topic_id)
        current_threat = tmp_threats[0] if tmp_threats else None

        if dependency_version:
            # collect vulnerables for this tag
            vulnerables_to_check = vulnerables_dict.get(tag.tag_name, set())
            if tag.parent_id and tag.parent_id != tag.tag_id:
                vulnerables_to_check |= vulnerables_dict.get(tag.parent_name, set())

            # detect how should be
            need_threat, need_ticket = False, False
            if not vulnerables_to_check:
                # topic is matched with this dependency on the tag, but have no actionable info
                need_threat, need_ticket = True, False
            else:
                for vulnerable in vulnerables_to_check:
                    try:
                        if vulnerable.detect_matched({dependency_version}):
                            # vulnerable and actionable
                            need_threat, need_ticket = True, True
                            break
                    except ValueError:
                        need_threat = True
                        # continue to find out actionable or not
        else:
            # dependency version is not comparable
            need_threat, need_ticket = True, False

        # fix threat and ticket
        if need_threat:
            if current_threat:
                threat = current_threat
            else:
                threat = models.Threat(
                    dependency_id=dependency.dependency_id, topic_id=topic.topic_id
                )
                persistence.create_threat(db, threat)
            if need_ticket:
                if not threat.ticket:
                    create_ticket_internal(db, threat, now=now)
            elif threat.ticket:
                persistence.delete_ticket(db, threat.ticket)
        elif current_threat:
            persistence.delete_threat(db, current_threat)

        db.flush()


def fix_threats_for_dependency(db: Session, dependency: models.Dependency):
    now = datetime.now()
    tag = dependency.tag
    package_family = PackageFamily.from_tag_name(tag.tag_name)
    try:
        dependency_version = gen_version_instance(package_family, dependency.version)
    except ValueError:
        # dependency.version is not comparable
        dependency_version = None

    if dependency_version:
        # collect TopicActions
        topic_actions: list[models.TopicAction] = []
        for topic in tag.topics:
            topic.actions.extend(topic.actions)

        # collect VulnerableRanges for each topics from TopicAction
        vulnerable_range_strings_dict: dict[str, set[str]] = {}  # topic_id: range strings
        for action in topic_actions:
            if not action.ext or not (vulnerable_versions := action.ext.get("vulnerable_versions")):
                continue
            for tag_name, vulnerable_range_strings in vulnerable_versions.items():
                if tag_name not in {tag.tag_name, tag.parent_name}:
                    continue
                if (tmp_str_set := vulnerable_range_strings_dict.get(action.topic_id)) is None:
                    tmp_str_set = set()
                    vulnerable_range_strings_dict[action.topic_id] = tmp_str_set
                for vulnerable_range_string in vulnerable_range_strings:
                    tmp_str_set |= set(vulnerable_range_string.split("||"))
        vulnerables_dict: dict[str, set[VulnerableRange]] = {}  # topic_id: VulnerableRanges
        for topic_id, vulnerable_range_strings in vulnerable_range_strings_dict.items():
            if (tmp_obj_set := vulnerables_dict.get(topic_id)) is None:
                tmp_obj_set = set()
                vulnerables_dict[topic_id] = tmp_obj_set
            for vulnerable_range_string in vulnerable_range_strings:
                try:
                    tmp_obj_set.add(
                        VulnerableRange.from_string(package_family, vulnerable_range_string)
                    )
                except ValueError:
                    pass  # ignore unexpected range strings

    # check and fix for each topics related to the dependency
    for topic_id in [topic.topic_id for topic in tag.topics]:
        tmp_threats = persistence.search_threats(db, dependency.dependency_id, topic_id)
        current_threat = tmp_threats[0] if tmp_threats else None

        if dependency_version:
            # get vulnerables for this topic
            vulnerables_to_check = vulnerables_dict.get(topic_id, set())

            # detect how should be
            need_threat, need_ticket = False, False
            if not vulnerables_to_check:
                # topic is matched with the dependency on the tag, but have no actionable info
                need_threat, need_ticket = True, False
            else:
                for vulnerable in vulnerables_to_check:
                    try:
                        if vulnerable.detect_matched({dependency_version}):
                            # vulnerable and actionable
                            need_threat, need_ticket = True, True
                            break
                    except ValueError:
                        need_threat = True
                        # continue to find out actionable or not
        else:
            # dependency version is not comparable
            need_threat, need_ticket = True, False

        # fix threat and ticket
        if need_threat:
            if current_threat:
                threat = current_threat
            else:
                threat = models.Threat(dependency_id=dependency.dependency_id, topic_id=topic_id)
                persistence.create_threat(db, threat)
            if need_ticket:
                if not threat.ticket:
                    create_ticket_internal(db, threat, now=now)
            elif threat.ticket:
                persistence.delete_ticket(db, threat.ticket)
        elif current_threat:
            persistence.delete_threat(db, current_threat)

import unicodedata
from datetime import datetime

from sqlalchemy.orm import Session

from app import models, persistence
from app.alert import send_alert_to_pteam
from app.ssvc import ssvc_calculator
from app.version import (
    PackageFamily,
    VulnerableRange,
    gen_version_instance,
)


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

    if ticket.current_ticket_status.topic_status == models.TopicStatusType.completed:
        return False

    pteam = ticket.threat.dependency.service.pteam
    return ticket.ssvc_deployer_priority <= pteam.alert_ssvc_priority


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
        ssvc_deployer_priority=ssvc_calculator.calculate_ssvc_priority_by_threat(threat),
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
            alert_content="",  # alert_content is not used
        )
        persistence.create_alert(db, alert)
        send_alert_to_pteam(alert)

    return ticket


def fix_threats_for_topic(db: Session, topic: models.Topic) -> list[str]:
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
    created_ticket_ids: list[str] = []
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
            need_ticket = False
            if not vulnerables_to_check:
                # topic is matched with this dependency on the tag, but have no actionable info
                need_ticket = False
            else:
                for vulnerable in vulnerables_to_check:
                    try:
                        if vulnerable.detect_matched({dependency_version}):
                            # vulnerable and actionable
                            need_ticket = True
                            break
                    except ValueError:
                        pass
                        # continue to find out actionable or not
        else:
            # dependency version is not comparable
            need_ticket = False

        # fix ticket
        if current_threat:
            threat = current_threat
        else:
            threat = models.Threat(dependency_id=dependency.dependency_id, topic_id=topic.topic_id)
            persistence.create_threat(db, threat)
        if need_ticket:
            if not threat.ticket:
                ticket = create_ticket_internal(db, threat, now=now)
                created_ticket_ids.append(ticket.ticket_id)
        elif threat.ticket:
            persistence.delete_ticket(db, threat.ticket)

        db.flush()
    return created_ticket_ids


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
            topic_actions.extend(topic.actions)

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
            need_ticket = False
            if not vulnerables_to_check:
                # topic is matched with the dependency on the tag, but have no actionable info
                need_ticket = False
            else:
                for vulnerable in vulnerables_to_check:
                    try:
                        if vulnerable.detect_matched({dependency_version}):
                            # vulnerable and actionable
                            need_ticket = True
                            break
                    except ValueError:
                        pass
                        # continue to find out actionable or not
        else:
            # dependency version is not comparable
            need_ticket = False

        # fix ticket
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


def fix_tickets_for_service(db: Session, service: models.Service):
    now = datetime.now()
    for ticket in service.tickets:
        fixed_priority = ssvc_calculator.calculate_ssvc_priority_by_threat(ticket.threat)
        if fixed_priority == ticket.ssvc_deployer_priority:
            continue
        ticket.ssvc_deployer_priority = fixed_priority
        # omit flush -- should be flushed in create_alert
        if ticket_meets_condition_to_create_alert(ticket):
            alert = models.Alert(
                ticket_id=ticket.ticket_id,
                alerted_at=now,
                alert_content="",  # not used currently
            )
            persistence.create_alert(db, alert)
            send_alert_to_pteam(alert)

    db.flush()


def count_ssvc_priority_from_summary(tags_summary: list[dict]):
    ssvc_priority_count: dict[models.SSVCDeployerPriorityEnum, int] = {
        priority: 0 for priority in list(models.SSVCDeployerPriorityEnum)
    }
    for tag_summary in tags_summary:
        ssvc_priority_count[
            tag_summary["ssvc_priority"] or models.SSVCDeployerPriorityEnum.DEFER
        ] += 1
    return ssvc_priority_count


def count_full_width_and_half_width_characters(string: str) -> int:
    count: int = 0
    for char in string:
        if unicodedata.east_asian_width(char) in "WFA":
            count += 2
        else:
            count += 1

    return count

from uuid import uuid4

USER1 = {  # see firebase/data-test/auth_export/accounts.json
    "email": "test1@example.com",
    "pass": "testpass1",  # see tail of passwordHash on accounts.json
    "disabled": False,
    "years": 2,
}
USER2 = {
    "email": "test2@example.com",
    "pass": "testpass2",
    "uid": "2UZpJaGjHjm8DPTv8I60sxLxqye8",
    "disabled": False,
    "years": 5,
}
USER3 = {
    "email": "test3@example.com",
    "pass": "testpass3",
    "uid": "Bh2Ed1qXyg5Gv362oMk9YXwdpiME",
    "disabled": False,
    "years": 2,
}
TAG1 = "alpha:alpha2:alpha3"
TAG2 = "bravo:bravo2:bravo3"
TAG3 = "charlie:charlie2:charlie3"
GROUP1 = "Threatconnectome"
GROUP2 = "RepoA"
REF1 = [
    {"target": "api/Pipfile.lock", "version": "1.0.0", "group": "Threatconnectome"},
    {"target": "api2/Pipfile.lock", "version": "1.0.1", "group": "Threatconnectome"},
    {"target": "api/Pipfile.lock", "version": "1.0.0", "group": "Flashsense"},
]
REF2 = [{"target": "web/package-lock.json", "version": "1.1.1", "group": "RepoA"}]
REF3 = [
    {
        "target": "Pipfile.lock",
        "version": "a1daed12b7955ab3ca423f7242a9ccfd249f2ebcba180a9376aea74b1ec913d0",
        "group": "productB",
    }
]

EXT_TAG1 = {
    "tag_name": TAG1,
    "references": REF1,
}
EXT_TAG2 = {
    "tag_name": TAG2,
    "references": REF2,
}
EXT_TAG3 = {
    "tag_name": TAG3,
    "references": REF3,
}
MISPTAG1 = "tlp:amber"
MISPTAG2 = "tlp:clear"
MISPTAG3 = "tlp:red"
PTEAM1 = {
    "pteam_name": "pteam alpha",
    "contact_info": "alpha@ml.com",
    "alert_slack": {"enable": True, "webhook_url": ""},
    "alert_threat_impact": 3,
    "alert_mail": {"enable": False, "address": "alpha@ml.com"},  # disable SendGrid if not needed
}

PTEAM2 = {
    "pteam_name": "pteam bravo",
    "contact_info": "bravo@ml.com",
    "alert_slack": {"enable": True, "webhook_url": ""},
    "alert_threat_impact": 2,
    "alert_mail": {"enable": False, "address": "bravo@ml.com"},  # disable SendGrid if not needed
}
PTEAM3 = {
    "pteam_name": "pteam charlie",
    "contact_info": "charlie@ml.com",
    "alert_slack": {"enable": True, "webhook_url": ""},
}
PTEAM4 = {
    "pteam_name": "pteam delta",
    "contact_info": "",
    "alert_slack": {"enable": True, "webhook_url": ""},
    "disabled": False,
}
ATEAM1 = {
    "ateam_name": "ateam a-one",
    "contact_info": "a-one@ml.com",
    "alert_mail": {"enable": False, "address": "a-one@ml.com"},  # disable SendGrid if not needed
}
ATEAM2 = {
    "ateam_name": "ateam a-two",
    "contact_info": "",
    "alert_mail": {"enable": False, "address": "a-two@ml.com"},  # disable SendGrid if not needed
}
TOPIC1 = {
    "topic_id": uuid4(),
    "title": "topic one",
    "abstract": "abstract one",
    "threat_impact": 1,
    "tags": [TAG1],
    "misp_tags": [MISPTAG1],
    "actions": [],
}
TOPIC2 = {
    "topic_id": uuid4(),
    "title": "topic two",
    "abstract": "abstract two",
    "threat_impact": 2,
    "tags": [TAG1],
    "misp_tags": [],
    "actions": [],
}
TOPIC3 = {
    "topic_id": uuid4(),
    "title": "topic three",
    "abstract": "abstract three",
    "threat_impact": 1,
    "tags": [TAG1, TAG3],
    "misp_tags": [],
    "actions": [],
}
TOPIC4 = {
    "topic_id": uuid4(),
    "title": "topic four",
    "abstract": "abstract four",
    "threat_impact": 2,
    "tags": [TAG3],
    "misp_tags": [],
    "actions": [],
}
ACTION1 = {
    "action": "action one",
    "action_type": "elimination",
    "recommended": True,
    "ext": {},
}
ACTION2 = {
    "action": "action two",
    "action_type": "mitigation",
    "recommended": False,
    "ext": {},
}
ACTION3 = {
    "action": "action three",
    "action_type": "rejection",
    "recommended": False,
    "ext": {},
}
ELIMINATED_ACTION = {
    "action": "eliminated action",
    "action_type": "elimination",
    "recommended": False,
    "ext": {},
}
MITIGATED_ACTION = {
    "action": "mitigated action",
    "action_type": "mitigation",
    "recommended": False,
    "ext": {},
}

SAMPLE_SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T00000000/B00000000/XXXX"

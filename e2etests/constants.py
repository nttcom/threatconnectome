USER1 = {  # see firebase/data-test/auth_export/accounts.json
    "email": "test1@example.com",
    "pass": "testpass1",  # see tail of passwordHash on accounts.json
    "uid": "2TXjRSTVkhjq4sbGOesYUJWdKwzj",  # localId on accounts.json
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
REF1 = [
    {"target": "api/Pipfile.lock", "version": "1.0.0", "service": "Threatconnectome"},
    {"target": "api2/Pipfile.lock", "version": "1.0.1", "service": "Threatconnectome"},
    {"target": "api/Pipfile.lock", "version": "1.0.0", "service": "Flashsense"},
]
REF2 = [{"target": "web/package-lock.json", "version": "1.1.1", "service": "RepoA"}]
REF3 = [
    {
        "target": "Pipfile.lock",
        "version": "a1daed12b7955ab3ca423f7242a9ccfd249f2ebcba180a9376aea74b1ec913d0",
        "service": "productB",
    }
]

PTEAM1 = {
    "pteam_name": "pteam alpha",
    "contact_info": "alpha@ml.com",
    "alert_ssvc_priority": "scheduled",
}

PTEAM2 = {
    "pteam_name": "pteam bravo",
    "contact_info": "bravo@ml.com",
    "alert_ssvc_priority": "out_of_cycle",
}
ACTION1 = {
    "action": "action one",
    "action_type": "elimination",
    "recommended": True,
}
ACTION2 = {
    "action": "action two",
    "action_type": "mitigation",
    "recommended": False,
}
ACTION3 = {
    "action": "action three",
    "action_type": "rejection",
    "recommended": False,
}

SAMPLE_SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T00000000/B00000000/XXXX"

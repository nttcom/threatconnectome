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
SERVICE1 = "Threatconnectome"
SERVICE2 = "RepoA"
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
    "alert_slack": {"enable": True, "webhook_url": ""},
    "alert_ssvc_priority": "scheduled",
    "alert_mail": {"enable": False, "address": "alpha@ml.com"},  # disable SendGrid if not needed
}

PTEAM2 = {
    "pteam_name": "pteam bravo",
    "contact_info": "bravo@ml.com",
    "alert_slack": {"enable": True, "webhook_url": ""},
    "alert_ssvc_priority": "out_of_cycle",
    "alert_mail": {"enable": False, "address": "bravo@ml.com"},  # disable SendGrid if not needed
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
PACKAGE1 = {
    "package_name": "axios",
    "ecosystem": "npm",
    "package_manager": "npm",
}
PACKAGE2 = {
    "package_name": "asynckit",
    "ecosystem": "npm",
    "package_manager": "npm",
}
PACKAGE3 = {
    "package_name": "combined-stream",
    "ecosystem": "npm",
    "package_manager": "npm",
}
VULNPACKAGE1 = {
    "affected_name": PACKAGE1["package_name"],
    "ecosystem": PACKAGE1["ecosystem"],
    "affected_versions": ["<2.0"],
    "fixed_versions": ["2.0"],
}
VULNPACKAGE2 = {
    "affected_name": PACKAGE2["package_name"],
    "ecosystem": PACKAGE2["ecosystem"],
    "affected_versions": ["<2.0"],
    "fixed_versions": ["2.0"],
}
VULNPACKAGE3 = {
    "affected_name": PACKAGE3["package_name"],
    "ecosystem": PACKAGE3["ecosystem"],
    "affected_versions": ["<2.0"],
    "fixed_versions": ["2.0"],
}
VULN1 = {
    "vuln_id": str(uuid4()),
    "cve_id": "CVE-0000-0001",
    "title": "Test Vulnerability1",
    "detail": "This is a test vulnerability.",
    "exploitation": "active",
    "automatable": "yes",
    "cvss_v3_score": 2.0,
    "vulnerable_packages": [VULNPACKAGE1],
}
VULN2 = {
    "vuln_id": str(uuid4()),
    "cve_id": "CVE-0000-0002",
    "title": "Test Vulnerability2",
    "detail": "This is a test vulnerability.",
    "exploitation": "active",
    "automatable": "yes",
    "cvss_v3_score": 2.0,
    "vulnerable_packages": [VULNPACKAGE2],
}
VULN3 = {
    "vuln_id": str(uuid4()),
    "cve_id": "CVE-0000-0002",
    "title": "Test Vulnerability2",
    "detail": "This is a test vulnerability.",
    "exploitation": "none",
    "automatable": "no",
    "cvss_v3_score": 2.0,
    "vulnerable_packages": [VULNPACKAGE3],
}

SAMPLE_SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T00000000/B00000000/XXXX"

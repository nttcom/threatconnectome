from uuid import uuid4

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
}
ACTION2 = {
    "action": "action two",
}
ACTION3 = {
    "action": "action three",
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

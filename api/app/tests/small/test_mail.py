from app import models
from app.notification.mail import create_mail_alert_for_new_vuln


def test_create_mail_alert_for_new_vuln_links_to_package_version_page():
    package_version_id = "72f764a3-f69e-4579-91fb-d80bc990cbf0"
    pteam_id = "70de29d6-2b33-4990-8d2a-657554335064"
    service_id = "4e74fbde-82fe-4d0a-a2bf-3c405c3b0814"

    _subject, body = create_mail_alert_for_new_vuln(
        vuln_title="test_title1",
        ssvc_priority=models.SSVCDeployerPriorityEnum.IMMEDIATE,
        pteam_name="team1",
        pteam_id=pteam_id,
        package_name="package1",
        ecosystem="npm",
        package_manager="npm",
        package_version_id=package_version_id,
        service_id=service_id,
        services=["service1"],
        asset_ip_addresses=None,
        asset_description=None,
    )

    expected_url = (
        f"http://localhost/package_versions/{package_version_id}"
        f"?pteamId={pteam_id}&serviceId={service_id}"
    )
    assert expected_url in body

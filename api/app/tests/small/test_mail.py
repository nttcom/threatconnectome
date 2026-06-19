from app import models
from app.notification.mail import (
    create_mail_alert_for_new_vuln,
    create_mail_to_notify_eol,
    create_mail_to_notify_sbom_upload_succeeded,
)


def test_create_mail_alert_for_new_vuln_links_to_package_version_page(monkeypatch):
    monkeypatch.setenv("WEBUI_URL", "https://example.com/app/")
    package_version_id = "72f764a3-f69e-4579-91fb-d80bc990cbf0"
    pteam_id = "70de29d6-2b33-4990-8d2a-657554335064"
    service_id = "4e74fbde-82fe-4d0a-a2bf-3c405c3b0814"

    _subject, body = create_mail_alert_for_new_vuln(
        vuln_title="test_title1",
        ssvc_priority=models.SSVCDeployerPriorityEnum.IMMEDIATE,
        pteam_name="team1",
        pteam_id=pteam_id,
        package_name="package <1> & package",
        ecosystem="npm",
        package_manager="npm",
        package_version_id=package_version_id,
        service_id=service_id,
        services=["service1"],
        asset_ip_addresses=None,
        asset_description=None,
    )

    expected_url = (
        f"https://example.com/app/package_versions/{package_version_id}"
        f"?pteamId={pteam_id}&serviceId={service_id}"
    )
    expected_href = expected_url.replace("&", "&amp;")
    assert (f'<a href="{expected_href}">' "Link to Package version page</a>") in body


def test_create_mail_to_notify_sbom_upload_succeeded_quotes_link_href(monkeypatch):
    monkeypatch.setenv("WEBUI_URL", "https://example.com/app/")
    pteam_id = "70de29d6-2b33-4990-8d2a-657554335064"
    service_id = "4e74fbde-82fe-4d0a-a2bf-3c405c3b0814"

    _subject, body = create_mail_to_notify_sbom_upload_succeeded(
        pteam_id=pteam_id,
        pteam_name="team1",
        service_id=service_id,
        service_name="service1",
        filename="test.cdx.json",
    )

    expected_href = f"https://example.com/app/?pteamId={pteam_id}&amp;serviceId={service_id}"
    assert f'<a href="{expected_href}">Link to the service tab</a>' in body


def test_create_mail_to_notify_eol_uses_link_to_eol_page_label(monkeypatch):
    monkeypatch.setenv("WEBUI_URL", "https://example.com/app/")
    pteam_id = "70de29d6-2b33-4990-8d2a-657554335064"

    _subject, body = create_mail_to_notify_eol(
        pteam_id=pteam_id,
        pteam_name="team1",
        service_name="service1",
        product_name="product <1> & product",
        version="1.0 <beta> & rc",
        eol_from="2026-06-19",
        asset_ip_addresses=None,
        asset_description=None,
    )

    expected_href = f"https://example.com/eol?pteamId={pteam_id}"
    assert f'<a href="{expected_href}">Link to EOL page</a>' in body

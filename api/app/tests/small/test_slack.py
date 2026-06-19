from urllib.parse import urlencode

from app import models
from app.notification.slack import (
    PACKAGE_VERSION_URL,
    SSVC_PRIORITY_LABEL,
    WEBUI_URL,
    create_slack_blocks_to_notify_eol,
    create_slack_blocks_to_notify_sbom_upload_succeeded,
    create_slack_pteam_alert_blocks_for_new_vuln,
)


def test_create_blocks_for_pteam():
    notification_data = {
        "pteam_id": "70de29d6-2b33-4990-8d2a-657554335064&team",
        "pteam_name": "team <1> & team",
        "package_name": "package <1> & package",
        "package_version_id": "72f764a3-f69e-4579-91fb-d80bc990cbf0",
        "vuln_id": "b1f74d1f-9360-4a8d-86ac-3cf5dd20c75c",
        "title": "test <title> & title",
        "ssvc_priority": models.SSVCDeployerPriorityEnum.IMMEDIATE,
        "service_id": "4e74fbde-82fe-4d0a-a2bf-3c405c3b0814&service",
        "services": ["test1 <service>", "test2 & service"],
        "asset_ip_addresses": ["192.168.0.1/32", "10.0.0.1/32"],
        "asset_description": "test <asset> & asset",
    }

    blocks = create_slack_pteam_alert_blocks_for_new_vuln(**notification_data)
    assert "team &lt;1&gt; &amp; team" in blocks[0]["text"]["text"]
    encoded_params = urlencode(
        {
            "pteamId": notification_data["pteam_id"],
            "serviceId": notification_data["service_id"],
        }
    )
    package_page_url = (
        f"{PACKAGE_VERSION_URL}{notification_data['package_version_id']}?{encoded_params}"
    )
    assert package_page_url in blocks[2]["text"]["text"]
    assert "package &lt;1&gt; &amp; package" in blocks[2]["text"]["text"]
    assert "test &lt;title&gt; &amp; title" in blocks[2]["text"]["text"]
    assert SSVC_PRIORITY_LABEL[notification_data["ssvc_priority"]] in blocks[2]["text"]["text"]
    assert "test1 &lt;service&gt;" in blocks[2]["text"]["text"]
    assert "test2 &amp; service" in blocks[2]["text"]["text"]
    assert notification_data["asset_ip_addresses"][0] in blocks[2]["text"]["text"]
    assert notification_data["asset_ip_addresses"][1] in blocks[2]["text"]["text"]
    assert "test &lt;asset&gt; &amp; asset" in blocks[2]["text"]["text"]


def test_create_blocks_to_notify_sbom_upload_succeeded_escapes_label_and_encodes_url():
    pteam_id = "70de29d6-2b33-4990-8d2a-657554335064&team"
    service_id = "4e74fbde-82fe-4d0a-a2bf-3c405c3b0814&service"

    blocks = create_slack_blocks_to_notify_sbom_upload_succeeded(
        pteam_id=pteam_id,
        pteam_name="team <1> & team",
        service_id=service_id,
        service_name="service <1> & service",
        uploaded_filename=None,
    )

    expected_url = f"{WEBUI_URL}?{urlencode({'pteamId': pteam_id, 'serviceId': service_id})}"
    assert f"<{expected_url}|service &lt;1&gt; &amp; service" in blocks[2]["text"]["text"]
    assert "team &lt;1&gt; &amp; team" in blocks[2]["text"]["text"]


def test_create_blocks_to_notify_eol_escapes_text_and_encodes_reference_url():
    pteam_id = "70de29d6-2b33-4990-8d2a-657554335064&team"

    blocks = create_slack_blocks_to_notify_eol(
        pteam_id=pteam_id,
        pteam_name="team <1> & team",
        service_name="service <1> & service",
        product_name="product <1> & product",
        version="1.0 <beta> & rc",
        eol_from="2026-06-19",
        asset_ip_addresses=["192.168.0.1/32"],
        asset_description="asset <1> & asset",
    )

    text = blocks[2]["text"]["text"]
    expected_params = urlencode({"pteamId": pteam_id})
    assert f"?{expected_params}" in text
    assert "team &lt;1&gt; &amp; team" in text
    assert "service &lt;1&gt; &amp; service" in text
    assert "product &lt;1&gt; &amp; product" in text
    assert "1.0 &lt;beta&gt; &amp; rc" in text
    assert "asset &lt;1&gt; &amp; asset" in text

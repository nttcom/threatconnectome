import os
from typing import Sequence
from urllib.parse import urlencode, urljoin

from fastapi import HTTPException, status
from slack_sdk.errors import SlackApiError
from slack_sdk.webhook import WebhookClient

from app import models

WEBUI_URL = os.getenv("WEBUI_URL", "http://localhost")
WEBUI_URL += "" if WEBUI_URL.endswith("/") else "/"  # for the case baseurl has subpath
# CAUTION: do *NOT* urljoin subpath which starts with "/"
PACKAGE_VERSION_URL = urljoin(WEBUI_URL, "package_versions/")
EOL_URL = urljoin(WEBUI_URL, "eol")
SSVC_PRIORITY_LABEL = {
    models.SSVCDeployerPriorityEnum.IMMEDIATE: ":red_circle: Immediate",
    models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE: ":large_orange_circle: Out-of-cycle",
    models.SSVCDeployerPriorityEnum.SCHEDULED: ":large_yellow_circle: Scheduled",
    models.SSVCDeployerPriorityEnum.DEFER: ":white_circle: Defer",
}


def validate_slack_webhook_url(url: str):
    hooks_url = "https://hooks.slack.com/services/"
    if not url.startswith(hooks_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid slack webhook url"
        )


def _mrkdwn_text(text: object) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _package_version_page_url(package_version_id: str, pteam_id: str, service_id: str) -> str:
    params = urlencode({"pteamId": str(pteam_id), "serviceId": str(service_id)})
    return urljoin(PACKAGE_VERSION_URL, str(package_version_id)) + f"?{params}"


def _block_header(text: str):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{_mrkdwn_text(text)}*",
            },
        },
        {"type": "divider"},
    ]


def send_slack(url: str, blocks: Sequence[dict]):
    try:
        webhook = WebhookClient(url)
        return webhook.send(text=blocks[0]["text"]["text"], blocks=blocks)
    except SlackApiError:
        return None


def create_slack_pteam_alert_blocks_for_new_vuln(
    pteam_id: str,
    pteam_name: str,
    package_version_id: str,
    package_name: str,
    package_version: str,
    vuln_id: str,
    title: str,
    ssvc_priority: models.SSVCDeployerPriorityEnum,
    service_id: str,
    services: list[str],
    asset_ip_addresses: list[str] | None,
    asset_description: str | None,
):
    blocks: list[dict[str, str | dict[str, str] | list[dict[str, str]]]]
    blocks = _block_header(text=pteam_name)
    package_url = _package_version_page_url(package_version_id, pteam_id, service_id)
    package_label = f"{package_name} {package_version}"
    services_name = ",".join(_mrkdwn_text(service) for service in services)
    ip_str = ", ".join(_mrkdwn_text(ip_address) for ip_address in asset_ip_addresses or []) or "-"
    desc_str = _mrkdwn_text(asset_description) if asset_description else "-"
    blocks.extend(
        [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join(
                        [
                            f"*Package URL*:<{package_url}|{_mrkdwn_text(package_label)}>",
                            f"*Title*:{_mrkdwn_text(title)}",
                            f"*Services*:{services_name}",
                            f"*SSVC Priority*:{SSVC_PRIORITY_LABEL[ssvc_priority]}",
                            "*Asset*:",
                            f"• IP Addresses: {ip_str}",
                            f"• Description: {desc_str}",
                        ]
                    ),
                },
            },
            {
                "type": "context",
                "elements": [{"type": "plain_text", "text": str(vuln_id)}],
            },
            {"type": "divider"},
        ]
    )
    return blocks


def create_slack_blocks_to_notify_sbom_upload_succeeded(
    pteam_id: str,
    pteam_name: str,
    service_id: str,
    service_name: str,
    uploaded_filename: str | None,
):
    blocks: list[dict[str, str | dict | list]] = _block_header(
        text=f":white_check_mark: SBOM uploaded as a service: {service_name}"
    )
    params = {"pteamId": pteam_id, "serviceId": service_id}
    encoded_params = urlencode(params)
    service_url = urljoin(WEBUI_URL, f"?{encoded_params}")
    blocks.extend(
        [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*<{service_url}|"
                        f"{_mrkdwn_text(service_name)} ({_mrkdwn_text(pteam_name)})>*"
                    ),
                },
            }
        ]
    )
    if uploaded_filename:
        blocks.extend(
            [
                {
                    "type": "context",
                    "elements": [{"type": "plain_text", "text": uploaded_filename}],
                },
            ]
        )
    return blocks


def create_slack_blocks_to_notify_sbom_upload_failed(
    service_name: str,
    uploaded_filename: str | None,
):
    blocks: list[dict[str, str | dict | list]] = _block_header(
        text=f":exclamation: Failed uploading SBOM as a service: {service_name}"
    )
    if uploaded_filename:
        blocks.extend(
            [
                {
                    "type": "context",
                    "elements": [{"type": "plain_text", "text": uploaded_filename}],
                },
            ]
        )
    return blocks


def create_slack_blocks_to_notify_eol(
    pteam_id: str,
    pteam_name: str,
    service_name: str,
    product_name: str,
    version: str,
    eol_from: str,
    asset_ip_addresses: list[str] | None,
    asset_description: str | None,
):
    blocks: list[dict[str, str | dict | list]] = _block_header(
        text=":warning: Action Required: migrate/upgrade to a supported version"
    )

    url = urljoin(EOL_URL, f"?{urlencode({'pteamId': str(pteam_id)})}")
    reference_label = f"{product_name} {version}"
    ip_str = ", ".join(_mrkdwn_text(ip_address) for ip_address in asset_ip_addresses or []) or "-"
    desc_str = _mrkdwn_text(asset_description) if asset_description else "-"
    blocks.extend(
        [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"EOL (End of Life) reached on *{_mrkdwn_text(eol_from)}* "
                        "(no more security fixes)\n\n"
                        f"*Service:* {_mrkdwn_text(service_name)}\n"
                        f"*Team:* {_mrkdwn_text(pteam_name)}\n"
                        f"*Product:* {_mrkdwn_text(product_name)}\n"
                        f"*Current Version:* {_mrkdwn_text(version)}\n"
                        f"*Asset:*\n"
                        f" • IP Addresses: {ip_str}\n"
                        f" • Description: {desc_str}\n"
                        f"*EOL Date:* {_mrkdwn_text(eol_from)}\n"
                        f"*Reference:* <{url}|{_mrkdwn_text(reference_label)}>"
                    ),
                },
            },
        ]
    )
    return blocks

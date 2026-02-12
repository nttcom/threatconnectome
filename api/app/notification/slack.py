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
PACKAGE_URL = urljoin(WEBUI_URL, "packages/")
EOL_URL = urljoin(WEBUI_URL, "eol/")
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


def _block_header(text: str):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{text}*",
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
    package_id: str,
    package_name: str,
    vuln_id: str,
    title: str,
    ssvc_priority: models.SSVCDeployerPriorityEnum,
    service_id: str,
    services: list[str],
):
    blocks: list[dict[str, str | dict[str, str] | list[dict[str, str]]]]
    blocks = _block_header(text=pteam_name)
    services_name = ",".join(services)
    blocks.extend(
        [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join(
                        [
                            f"*<{PACKAGE_URL}{str(package_id)}?pteamId={pteam_id}&serviceId={service_id}|{package_name}>*",
                            f"*{title}*",
                            f"*{services_name}*",
                            SSVC_PRIORITY_LABEL[ssvc_priority],
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
                    "text": f"*<{service_url}|{service_name} ({pteam_name})>*",
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
):
    blocks: list[dict[str, str | dict | list]] = _block_header(
        text=":warning: Action Required: migrate/upgrade to a supported version"
    )

    url = urljoin(EOL_URL, f"?pteamId={pteam_id}")
    blocks.extend(
        [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"EOL (End of Life) reached on *<{eol_from}>* (no more security fixes)\n\n"
                        f"• *Service:* {service_name}\n"
                        f"• *Team:* {pteam_name}\n"
                        f"• *Product:* {product_name}\n"
                        f"• *Current Version:* {version}\n"
                        f"• *EOL Date:* {eol_from}\n"
                        f"• *Reference:* {url}"
                    ),
                },
            },
        ]
    )
    return blocks

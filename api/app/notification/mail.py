import os
from urllib.parse import urlencode, urljoin
from uuid import UUID

from app import models


def _package_page_link(pteam_id: UUID | str, package_id: UUID | str, service_id: UUID | str) -> str:
    return urljoin(
        os.getenv("WEBUI_URL", "http://localhost"),
        f"/packages/{str(package_id)}?pteamId={str(pteam_id)}&serviceId={str(service_id)}",
    )


def _pteam_service_tab_link(pteam_id: UUID | str, service_id: UUID | str) -> str:
    baseurl = os.getenv("WEBUI_URL", "http://localhost")
    baseurl += "" if baseurl.endswith("/") else "/"
    params = {"pteamId": str(pteam_id), "serviceId": str(service_id)}
    encoded_params = urlencode(params)
    return urljoin(baseurl, f"?{encoded_params}")


def create_mail_alert_for_new_vuln(
    vuln_title: str,
    ssvc_priority: models.SSVCDeployerPriorityEnum,
    pteam_name: str,
    pteam_id: UUID | str,
    package_name: str,
    ecosystem: str,
    package_manager: str,
    package_id: UUID | str,
    service_id: UUID | str,
    services: list[str],
) -> tuple[str, str]:  # subject, body
    ssvc_priority_label = {
        models.SSVCDeployerPriorityEnum.IMMEDIATE: "Immediate",
        models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE: "Out-of-cycle",
        models.SSVCDeployerPriorityEnum.SCHEDULED: "Scheduled",
        models.SSVCDeployerPriorityEnum.DEFER: "Defer",
    }.get(ssvc_priority) or "Defer"
    subject = f"[Tc Alert] {ssvc_priority_label}: {vuln_title}"
    body = "<br>".join(
        [
            "A new vuln created.",
            "",
            f"Title: {vuln_title}",
            f"SSVC Priority: {ssvc_priority_label}",
            "",
            f"Team: {pteam_name}",
            f"Services: {', '.join(services)}",
            f"Package: {package_name}",
            f"Ecosystem: {ecosystem}",
            f"Package Manager: {package_manager}",
            "",
            (
                f"<a href={_package_page_link(pteam_id, package_id, service_id)}>Link to"
                " Package page</a>"
            ),
        ]
    )
    return subject, body


def create_mail_to_notify_sbom_upload_succeeded(
    pteam_id: UUID | str,
    pteam_name: str,
    service_id: UUID | str,
    service_name: str,
    filename: str | None,
) -> tuple[str, str]:  # subject, body
    subject = f"[Tc Info] SBOM uploaded as a service: {service_name}"
    body = "<br>".join(
        [
            "SBOM upload successfully ended.",
            "",
            f"PTeamName: {pteam_name}",
            f"ServiceName: {service_name}",
            "",
            f"<a href={_pteam_service_tab_link(pteam_id, service_id)}>Link to the service tab</a>",
            "",
            f"UploadedFilename: {filename or '(unknown)'}",
        ]
    )
    return subject, body


def create_mail_to_notify_sbom_upload_failed(
    service_name: str,
    filename: str | None,
) -> tuple[str, str]:  # subject, body
    subject = f"[Tc Error] SBOM upload failed as a service: {service_name}"
    body = "<br>".join(
        [
            "SBOM upload failed.",
            "",
            f"ServiceName: {service_name}",
            f"UploadedFilename: {filename or '(unknown)'}",
        ]
    )
    return subject, body


def create_mail_to_notify_eol(
    pteam_name: str,
    service_name: str,
    product_name: str,
    version: str,
    eol_from: str,
) -> tuple[str, str]:
    # TODO: Once the EOL link is confirmed, implement the URL.
    subject = "[Tc Warning] Action Required: migrate/upgrade to a supported version"
    body = "<br>".join(
        [
            f"EOL (End of Life) reached on <b><{eol_from}></b> (no more security fixes)",
            "",
            "<ul>",
            f"<li><b>Service:</b> {service_name}</li>",
            f"<li><b>Team:</b> {pteam_name}</li>",
            f"<li><b>Product:</b> {product_name}</li>",
            f"<li><b>Current Version:</b> {version}</li>",
            f"<li><b>EOL Date:</b> {eol_from}</li>",
            # f"<li><b>Reference:</b> <a href='{url}'>{url}</a></li>",
            "</ul>",
        ]
    )
    return subject, body

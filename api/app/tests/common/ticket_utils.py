from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.main import app
from app.routers.pteams import bg_create_tags_from_sbom_json
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    create_vuln,
)

client = TestClient(app)


def create_ticket(testdb: Session, user: dict, pteam: dict, service_name: str, vuln: dict):
    user1 = create_user(user)
    pteam1 = create_pteam(user, pteam)

    # Uploaded sbom file.
    # Create package, package_version, service and dependency table
    upload_file_name = "test_trivy_cyclonedx_axios.json"
    sbom_file = Path(__file__).resolve().parent / "upload_test" / upload_file_name
    with open(sbom_file, "r") as sbom:
        sbom_json = sbom.read()

    bg_create_tags_from_sbom_json(sbom_json, pteam1.pteam_id, service_name, upload_file_name)

    # Create vuln and affect table
    vuln1 = create_vuln(user, vuln)

    # Saerch service table
    service_id = testdb.scalars(
        select(models.Service.service_id).where(
            models.Service.pteam_id == str(pteam1.pteam_id),
            models.Service.service_name == service_name,
        )
    ).one()

    # Search package_version table
    package_version = testdb.scalars(select(models.PackageVersion)).one()

    # Search ticket table
    ticket = testdb.scalars(select(models.Ticket)).one()

    return {
        "user_id": str(user1.user_id),
        "pteam_id": str(pteam1.pteam_id),
        "service_id": str(service_id),
        "package_id": str(package_version.package_id),
        "package_version_id": str(package_version.package_version_id),
        "vuln_id": str(vuln1.vuln_id),
        "threat_id": str(ticket.threat.threat_id),
        "ticket_id": str(ticket.ticket_id),
    }

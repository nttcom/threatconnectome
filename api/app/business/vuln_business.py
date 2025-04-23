import json
from hashlib import md5

from app import models


def calculate_content_fingerprint_by_vuln(vuln: models.Vuln) -> str:
    data = _get_vuln_data_for_fingerprint(vuln.title, vuln.detail, vuln.cvss_v3_score, vuln.affects)
    return md5(json.dumps(data, sort_keys=True).encode()).hexdigest()


def calculate_content_fingerprint(
    vuln_title: str, vuln_detail: str, cvss_v3_score: float | None, affects: list[models.Affect]
) -> str:
    data = _get_vuln_data_for_fingerprint(vuln_title, vuln_detail, cvss_v3_score, affects)
    return md5(json.dumps(data, sort_keys=True).encode()).hexdigest()


def _get_vuln_data_for_fingerprint(
    vuln_title: str, vuln_detail: str, cvss_v3_score: float | None, affects: list[models.Affect]
) -> dict:
    sorted_affects = sorted(
        affects, key=lambda affect: (affect.package.name, affect.package.ecosystem)
    )
    return {
        "title": vuln_title,
        "detail": vuln_detail,
        "cvss_v3_score": cvss_v3_score,
        "affects": [_get_affect_data_for_fingerprint(affect) for affect in sorted_affects],
    }


def _get_affect_data_for_fingerprint(affect: models.Affect) -> dict:
    return {
        "package_name": affect.package.name,
        "ecosystem": affect.package.ecosystem,
        "affected_versions": sorted(affect.affected_versions),
        "fixed_versions": sorted(affect.fixed_versions),
    }

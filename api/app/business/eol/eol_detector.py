from app import models
from app.business.eol import eol_version_factory

from .version.EoLBaseVersion import EoLBaseVersion


def check_matched_package_version_and_eol_version(
    package_version: models.PackageVersion, eol_version: models.EoLVersion
) -> bool:
    package = package_version.package
    try:
        version: EoLBaseVersion = eol_version_factory.gen_version_instance_for_eol(
            eol_version.eol_product.name, package_version.version, package.vuln_matching_ecosystem
        )
    except ValueError:
        return False

    return eol_version.matching_version == version.get_version()

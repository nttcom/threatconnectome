from app import models
from app.business.eol.ecosystem import eol_ecosystem_factory
from app.business.eol.product import eol_product_factory
from app.business.eol.version import eol_version_factory

from .ecosystem.eol_base_ecosystem import EoLBaseEcosystem
from .product.eol_base_product import EoLBaseProduct
from .version.eol_base_version import EoLBaseVersion


def match_eol_for_ecosystem(
    package: models.Package,
    eol_version: models.EoLVersion,
) -> bool:
    eol_ecosystem: EoLBaseEcosystem = eol_ecosystem_factory.gen_ecosystem_instance_for_eol(
        eol_version.eol_product.name
    )
    return eol_ecosystem.match_ecosystem(package.ecosystem, eol_version.version)


def match_eol_for_product(
    package_version: models.PackageVersion,
    eol_product: models.EoLProduct,
    eol_version: models.EoLVersion,
) -> bool:
    return _check_matched_package_version_and_eol_product(
        package_version, eol_product
    ) and _check_matched_package_version_and_eol_version(package_version, eol_version)


def _check_matched_package_version_and_eol_product(
    package_version: models.PackageVersion, eol_product: models.EoLProduct
) -> bool:
    package = package_version.package
    product: EoLBaseProduct = eol_product_factory.gen_product_instance_for_eol(
        eol_product, package.ecosystem
    )
    return product.match_package(package_version.package.name, package_version.version)


def _check_matched_package_version_and_eol_version(
    package_version: models.PackageVersion, eol_version: models.EoLVersion
) -> bool:
    package = package_version.package
    try:
        version: EoLBaseVersion = eol_version_factory.gen_version_instance_for_eol(
            eol_version.eol_product.name, package_version.version, package.ecosystem
        )
    except ValueError:
        return False

    # match if any candidate version matches the eol cycle
    return eol_version.version in version.get_versions()

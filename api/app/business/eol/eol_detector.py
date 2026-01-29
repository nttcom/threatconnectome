from app import models
from app.business.eol.product import eol_product_factory
from app.business.eol.version import eol_version_factory

from .product.EoLBaseProduct import EoLBaseProduct
from .version.EoLBaseVersion import EoLBaseVersion


def get_eol_product_packages(eol_product: models.EoLProduct) -> list[str]:
    product: EoLBaseProduct = eol_product_factory.gen_product_instance_for_eol(eol_product)
    return product.get_packages()


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

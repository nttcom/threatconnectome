from typing import Sequence

from sqlalchemy.orm import Session

from app import models, persistence, schemas


def fix_package(db: Session, package: models.Package) -> None:
    is_referenced_by_dependency = False
    for package_version in package.package_versions:
        if len(package_version.dependencies) == 0:
            persistence.delete_package_version(db, package_version)
        else:
            is_referenced_by_dependency = True
    if is_referenced_by_dependency or len(package.affects) > 0:
        return
    persistence.delete_package(db, package)


def get_pteam_ext_packages(pteam: models.PTeam) -> Sequence[schemas.PackageFileResponse]:
    ext_packages_dict: dict[str, schemas.PackageFileResponse] = {}
    for service in pteam.services:
        for dependency in service.dependencies:
            ext_package = ext_packages_dict.get(
                dependency.package_version.package_id,
                schemas.PackageFileResponse(
                    package_id=dependency.package_version.package_id,
                    package_name=dependency.package_version.package.name,
                    ecosystem=dependency.package_version.package.ecosystem,
                    references=[],
                ),
            )

            ext_package.references.append(
                schemas.PackageFileResponse.Reference(
                    service=service.service_name,
                    target=dependency.target,
                    package_manager=dependency.package_manager,
                    version=dependency.package_version.version,
                ),
            )
            ext_packages_dict[dependency.package_version.package_id] = ext_package

    return sorted(ext_packages_dict.values(), key=lambda x: (x.package_name, x.ecosystem))

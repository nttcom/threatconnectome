from univers.versions import InvalidVersion

from .EoLBaseVersion import EoLBaseVersion
from .MajorOnlyVersion import MajorOnlyVersion


def gen_version_instance_for_eol(
    product: str,
    version_string: str,
    ecosystem: str,
) -> EoLBaseVersion:
    try:
        match product:
            case "firefox":
                return MajorOnlyVersion(version_string, ecosystem)
            case "sqlite":
                return MajorOnlyVersion(version_string, ecosystem)
            case _:
                return EoLBaseVersion(version_string)
    except InvalidVersion:
        raise ValueError(
            f"Invalid version string for product '{product}' "
            f"with ecosystem '{ecosystem}': {version_string}"
        )

from univers.versions import InvalidVersion

from .EoLBaseVersion import EoLBaseVersion
from .MajorAndMinorVersion import MajorAndMinorVersion
from .MajorOnlyVersion import MajorOnlyVersion
from .MajorOrMajorAndMinorVersion import MajorOrMajorAndMinorVersion


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
            case "react":
                return MajorOnlyVersion(version_string, ecosystem)
            case "postgresql":
                return MajorOnlyVersion(version_string, ecosystem)
            case "nodejs":
                return MajorOnlyVersion(version_string, ecosystem)
            case "amazon-corretto":
                return MajorOnlyVersion(version_string, ecosystem)
            case "redis":
                return MajorAndMinorVersion(version_string, ecosystem)
            case "django":
                return MajorAndMinorVersion(version_string, ecosystem)
            case "numpy":
                return MajorAndMinorVersion(version_string, ecosystem)
            case "php":
                return MajorAndMinorVersion(version_string, ecosystem)
            case "python":
                return MajorAndMinorVersion(version_string, ecosystem)
            case "ruby":
                return MajorAndMinorVersion(version_string, ecosystem)
            case "ansible":
                return MajorOrMajorAndMinorVersion(version_string, ecosystem)
            case _:
                return EoLBaseVersion(version_string)
    except InvalidVersion:
        raise ValueError(
            f"Invalid version string for product '{product}' "
            f"with ecosystem '{ecosystem}': {version_string}"
        )

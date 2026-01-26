from univers.versions import InvalidVersion

from .version.EoLBaseVersion import EoLBaseVersion
from .version.FirefoxVersion import FirefoxVersion


def gen_version_instance_for_eol(
    product: str,
    version_string: str,
    ecosystem: str,
) -> EoLBaseVersion:
    try:
        match product:
            case "firefox":
                return FirefoxVersion(version_string, ecosystem)
            case _:
                return EoLBaseVersion(version_string)
    except InvalidVersion:
        raise ValueError(f"Invalid version string: {version_string}")

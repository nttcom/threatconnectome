from .eol_alma_linux_ecosystem import EoLAlmaLinuxEcosystem
from .eol_alpine_ecosystem import EoLAlpineEcosystem
from .eol_base_ecosystem import EoLBaseEcosystem
from .eol_rocky_ecosystem import EoLRockyEcosystem


def gen_ecosystem_instance_for_eol(
    product: str,
) -> EoLBaseEcosystem:
    match product:
        case "alpine-linux":
            return EoLAlpineEcosystem(product)
        case "rocky-linux":
            return EoLRockyEcosystem(product)
        case "almalinux":
            return EoLAlmaLinuxEcosystem(product)
        case _:
            return EoLBaseEcosystem(product)

from .EoLAlmaLinuxEcosystem import EoLAlmaLinuxEcosystem
from .EoLAlpineEcosystem import EoLAlpineEcosystem
from .EoLBaseEcosystem import EoLBaseEcosystem
from .EoLRockyEcosystem import EoLRockyEcosystem


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

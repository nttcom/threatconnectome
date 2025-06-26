OS_TYPES = [
    "alma",
    "alpine",
    "amazon",
    "azurelinux",
    "bottlerocket",
    "cbl-mariner",
    "centos",
    "chainguard",
    "debian",
    "echo",
    "fedora",
    "minimos",
    "opensuse",
    "opensuse-leap",
    "opensuse-tumbleweed",
    "oracle",
    "photon",
    "redhat",
    "rocky",
    "slem",
    "sles",
    "ubuntu",
    "wolfi",
]


def is_os_ecosystem(ecosystem: str) -> bool:
    if not ecosystem:
        return False
    return any(ecosystem.startswith(type) for type in OS_TYPES)

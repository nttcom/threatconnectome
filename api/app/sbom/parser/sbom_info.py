from typing import (
    NamedTuple,
)


class SBOMInfo(NamedTuple):
    spec_name: str
    spec_version: str
    tool_name: str
    tool_version: str | None

from os import environ
from uuid import UUID

# system reserved data
MEMBER_UUID: UUID = UUID(int=0xCAFE0001)
NOT_MEMBER_UUID: UUID = UUID(int=0xCAFE0002)

SYSTEM_UUID: UUID = UUID(int=0xCAFE0011)
SYSTEM_EMAIL: str = environ.get("SYSTEM_EMAIL") or "SYSTEM_ACCOUNT"

# default value
DEFAULT_ALERT_SSVC_PRIORITY: str = "immediate"

# sample data
ZERO_FILLED_UUID: UUID = UUID("00000000-0000-0000-0000-000000000000")

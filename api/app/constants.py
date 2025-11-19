from os import environ
from uuid import UUID

SYSTEM_EMAIL: str = environ.get("SYSTEM_EMAIL") or "SYSTEM_ACCOUNT"

# default value
DEFAULT_ALERT_SSVC_PRIORITY: str = "immediate"

# character count limits
MAX_WEBHOOK_URL_LENGTH_IN_HALF: int = 255
MAX_EMAIL_ADDRESS_LENGTH_IN_HALF: int = 255

# sample data
ZERO_FILLED_UUID: UUID = UUID("00000000-0000-0000-0000-000000000000")

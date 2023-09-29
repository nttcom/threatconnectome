from requests.models import Response


class HTTPError(Exception):
    code: int
    reason: str

    def __init__(self, response: Response):
        super().__init__()
        self.code = response.status_code
        self.reason = response.reason

    def __str__(self) -> str:
        return f"{self.code}: {self.reason}"
